import React, {FunctionComponent} from 'react'
import {Route, Switch} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {history, useAppDispatch} from '../store'
import {refreshStatus} from '../reducers/status'

import AuthenticatedRoute from './AuthenticatedRoute'
import About from './About'
import GettingStarted from './GettingStarted'
import Configure from './Configure'
import Tasks from './Tasks'
import RedirectToFirstTask from './RedirectToFirstTask'

const App: FunctionComponent = () => {
  const dispatch = useAppDispatch()
  dispatch(refreshStatus())

  return (
    <ConnectedRouter history={history}>
      <Switch>
        <AuthenticatedRoute
          exact
          path="/getting-started"
          component={GettingStarted}
        />
        <AuthenticatedRoute exact path="/configuration" component={Configure} />
        <AuthenticatedRoute exact path="/tasks/:taskId" component={Tasks} />
        <AuthenticatedRoute
          exact
          path="/tasks"
          component={RedirectToFirstTask}
        />
        <Route path="/" component={About} />
      </Switch>
    </ConnectedRouter>
  )
}

export default App
