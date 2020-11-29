import React, {FunctionComponent} from 'react'
import {Redirect, Route, Switch} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {useToasts} from 'react-toast-notifications'
import {useSelector} from 'react-redux'

import AuthenticatedRoute from './AuthenticatedRoute'
import About from './About'
import GettingStarted from './GettingStarted'
import Tasks from './Tasks'
import MobileTasks from './MobileTasks'
import ActivityLog from './ActivityLog'
import RedirectToFirstTask from './RedirectToFirstTask'
import Configure from './Configure'
import {RootState, history, useAppDispatch} from '../store'
import {statusActions} from '../reducers'
import {StreamEventType, getMessage} from '../clients/stream'
import {Stream} from '../contexts/stream'
import {refreshTask, refreshTasks} from '../thunks/tasks'

const AppRouter: FunctionComponent = () => {
  const dispatch = useAppDispatch()
  const streamState = React.useContext(Stream)
  const {addToast} = useToasts()
  const stylesheet = useSelector((state: RootState) =>
    state.status.logged_in === true ? state.status.colorscheme : null
  )

  React.useEffect(() => {
    const stylesheetId = 'colorscheme-stylesheet'

    if (stylesheet) {
      const existing = document.getElementById(stylesheetId)
      if (existing) {
        existing.remove()
      }

      const sheet = document.createElement('link')
      sheet.rel = 'stylesheet'
      sheet.href = `/assets/colorschemes/${stylesheet}.css`
      sheet.id = stylesheetId
      document.head.appendChild(sheet)
    }
  }, [stylesheet])

  React.useEffect(() => {
    if (streamState.stream) {
      streamState.stream.addEventListener(
        StreamEventType.HeadChanged,
        (evt: Event) => {
          const head = getMessage(StreamEventType.HeadChanged, evt)
          dispatch(statusActions.headChanged(head))
        }
      )
      streamState.stream.addEventListener(
        StreamEventType.PersonalAnnouncement,
        (evt: Event) => {
          const msg = getMessage(StreamEventType.PersonalAnnouncement, evt)

          addToast(
            <>
              <b>{msg.title}</b>:{msg.message}
            </>,
            {
              appearance: msg.type,
            }
          )
        }
      )
      streamState.stream.addEventListener(
        StreamEventType.PublicAnnouncement,
        (evt: Event) => {
          const msg = getMessage(StreamEventType.PublicAnnouncement, evt)

          addToast(
            <>
              <b>{msg.title}</b>:{msg.message}
            </>,
            {
              appearance: msg.type,
            }
          )
        }
      )
      streamState.stream.addEventListener(
        StreamEventType.TaskChanged,
        (evt: Event) => {
          const taskId = getMessage(StreamEventType.TaskChanged, evt)
          dispatch(refreshTask(taskId))
        }
      )
    }
  }, [streamState.stream])

  React.useEffect(() => {
    dispatch(refreshTasks())
  }, [])

  return (
    <ConnectedRouter history={history}>
      <Switch>
        <AuthenticatedRoute
          exact
          path="/getting-started"
          component={GettingStarted}
        />
        <Route
          exact
          path="/configure"
          render={() => <Redirect to="/configure/synchronization" />}
        />
        <AuthenticatedRoute
          exact
          path="/configure/:page"
          component={Configure}
        />
        <AuthenticatedRoute exact path="/task-list" component={MobileTasks} />
        <AuthenticatedRoute exact path="/tasks/:taskId" component={Tasks} />
        <AuthenticatedRoute
          exact
          path="/tasks"
          component={RedirectToFirstTask}
        />
        <AuthenticatedRoute
          exact
          path="/activity-log"
          component={ActivityLog}
        />
        <Route path="/" component={About} />
      </Switch>
    </ConnectedRouter>
  )
}

export default AppRouter
