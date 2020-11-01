import React, {FunctionComponent} from 'react'
import {Route, Switch} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {history, useAppDispatch} from '../store'
import {refreshStatus} from '../reducers/status'

import About from './About'
import GettingStarted from './GettingStarted'
import Configure from './Configure'
import Tasks from './Tasks'

const App: FunctionComponent = () => {
  const dispatch = useAppDispatch()
  dispatch(refreshStatus())

  return (
    <ConnectedRouter history={history}>
      <Switch>
        <Route exact path="/getting-started" component={GettingStarted} />
        <Route exact path="/configuration" component={Configure} />
        <Route exact path="/tasks" component={Tasks} />
        <Route path="/" component={About} />
      </Switch>
    </ConnectedRouter>
  )
}

export default App
