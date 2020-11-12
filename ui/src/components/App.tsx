import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Route, Switch} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {history, useAppDispatch} from '../store'
import {refreshStatus} from '../reducers/status'
import {ToastProvider} from 'react-toast-notifications'

import AnnotationModal from './modals/AnnotationModal'
import AuthenticatedRoute from './AuthenticatedRoute'
import About from './About'
import GettingStarted from './GettingStarted'
import Configure from './Configure'
import Tasks from './Tasks'
import RedirectToFirstTask from './RedirectToFirstTask'
import {RootState} from '../store'
import EditTaskModal from './modals/EditTaskModal'

const App: FunctionComponent = () => {
  const loggedIn = useSelector((state: RootState) => state.status.logged_in)
  const dispatch = useAppDispatch()

  dispatch(refreshStatus)

  return (
    <>
      {/* Checking for null here to prevent us from processing routes
          until we know whether (or not) the user is logged-in -- otherwise
          we might redirect folks to the 'About' or ''Redirect to first task'
          when we really don't need to do so
      */}
      {loggedIn !== null && (
        <>
          <ToastProvider placement={'top-center'} autoDismiss={true}>
            <ConnectedRouter history={history}>
              <Switch>
                <AuthenticatedRoute
                  exact
                  path="/getting-started"
                  component={GettingStarted}
                />
                <AuthenticatedRoute
                  exact
                  path="/configuration"
                  component={Configure}
                />
                <AuthenticatedRoute
                  exact
                  path="/tasks/:taskId"
                  component={Tasks}
                />
                <AuthenticatedRoute
                  exact
                  path="/tasks"
                  component={RedirectToFirstTask}
                />
                <Route path="/" component={About} />
              </Switch>
            </ConnectedRouter>
            <AnnotationModal />
            <EditTaskModal />
          </ToastProvider>
        </>
      )}
    </>
  )
}

export default App
