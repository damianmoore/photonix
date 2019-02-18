import React from 'react'
import { BrowserRouter as Router, Route } from 'react-router-dom'
import ApolloClient from 'apollo-boost'
import { ApolloProvider } from 'react-apollo'
import 'normalize.css'
import '../static/css/App.css'
import BrowseContainer from '../containers/BrowseContainer'
import PhotoDetailContainer from '../containers/PhotoDetailContainer'
import ComponentsBrowser from '../components/ComponentsBrowser'


const client = new ApolloClient()

const App = ({ selectedFilters, onFilterToggle }) => (
  <ApolloProvider client={client}>
    <Router>
      <div>
        <Route path="/" exact render={(params) => <BrowseContainer selectedFilters={selectedFilters} search={params.location.search} onFilterToggle={onFilterToggle} />} />
        <Route path="/photo/:photoId" render={(params) => <PhotoDetailContainer photoId={params.match.params.photoId} />} />
        <Route path="/components" exact render={(params) => <ComponentsBrowser />} />
      </div>
    </Router>
  </ApolloProvider>
)

export default App
