import hashlib
import json
import lzma
import os
import random
import shutil
import subprocess
import tempfile

from django.conf import settings
import redis
from redis_lock import Lock
import requests


r = redis.Redis(host=os.environ.get('REDIS_HOST', '127.0.0.1'))
graph_cache = {}


class BaseModel:
    def __init__(self):
        global graph_cache
        self.graph_cache = graph_cache

    def ensure_downloaded(self):
        if self.name in self.graph_cache:
            return True

        version_file = os.path.join(settings.MODEL_DIR, self.name, 'version.txt')

        with Lock(r, 'classifier_{}_download'.format(self.name)):
            try:
                with open(version_file) as f:
                    if f.read().strip() == str(self.version):
                        return True
            except FileNotFoundError:
                pass

            response = requests.get(settings.MODEL_INFO_URL)
            models_info = json.loads(response.content)
            model_info = models_info[self.name][str(self.version)]
            error = False

            for file_data in model_info['files']:
                final_path = os.path.join(settings.MODEL_DIR, self.name, file_data['filename'])
                if not os.path.exists(final_path):
                    locations = file_data['locations']
                    index = random.choice(range(len(locations)))
                    location = locations.pop(index)
                    hash_sha256 = hashlib.sha256()
                    request = requests.get(location, stream=True)

                    if request.status_code != 200:
                        error = True
                        continue

                    # Download file to temporary location
                    with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as f:
                        for chunk in request.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                            if chunk:  # filter out keep-alive new chunks
                                f.write(chunk)
                                hash_sha256.update(chunk)

                    # Move file to correct location if the hash matches
                    if hash_sha256.hexdigest() == file_data['sha256']:
                        dirname = os.path.dirname(final_path)
                        if not os.path.isdir(dirname):
                            os.mkdir(dirname)

                        if file_data.get('decompress'):
                            if file_data['filename'].endswith('.xz'):
                                xz_path = '{}.xz'.format(f.name)
                                shutil.move(f.name, xz_path)
                                subprocess.run(['unxz', xz_path])
                                final_path = final_path.replace('.xz', '')

                        shutil.move(f.name, final_path)
                    else:
                        error = True
                        # TODO: Delete badly downloaded file

            # Write version file
            with open(version_file, 'w') as f:
                if error:
                    f.write('ERROR\n')
                    return False
                else:
                    f.write('{}\n'.format(str(self.version)))
                    return True
