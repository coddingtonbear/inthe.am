import React, {FunctionComponent} from 'react'
import {Route, Switch, Redirect} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {history} from '../store'

import About from './About'

const App: FunctionComponent = () => {
  return (
    <ConnectedRouter history={history}>
      <Switch>
        <Route path="/">
          <About />
        </Route>
      </Switch>
    </ConnectedRouter>
  )
}

export default App
