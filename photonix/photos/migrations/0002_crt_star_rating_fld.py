# Generated by Django 3.0.7 on 2020-12-23 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='star_rating',
            field=models.PositiveIntegerField(default=0, help_text='assign rating to photo', verbose_name='Rating'),
        ),
    ]
