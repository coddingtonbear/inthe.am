import React, {FunctionComponent} from 'react'
import {Route, Switch} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {history} from '../store'

import About from './About'
import GettingStarted from './GettingStarted'
import Configure from './Configure'

const App: FunctionComponent = () => {
  return (
    <ConnectedRouter history={history}>
      <Switch>
        <Route exact path="/getting-started" component={GettingStarted} />
        <Route exact path="/configuration" component={Configure} />
        <Route path="/" component={About} />
      </Switch>
    </ConnectedRouter>
  )
}

export default App
