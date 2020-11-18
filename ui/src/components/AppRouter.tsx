import React, {FunctionComponent} from 'react'
import {Route, Switch} from 'react-router'
import {ConnectedRouter} from 'connected-react-router/immutable'
import {useToasts} from 'react-toast-notifications'

import AuthenticatedRoute from './AuthenticatedRoute'
import About from './About'
import GettingStarted from './GettingStarted'
import Configure from './Configure'
import Tasks from './Tasks'
import ActivityLog from './ActivityLog'
import RedirectToFirstTask from './RedirectToFirstTask'
import {history, useAppDispatch} from '../store'
import {statusActions} from '../reducers'
import {StreamEventType, getMessage} from '../clients/stream'
import {Stream} from '../contexts/stream'

const AppRouter: FunctionComponent = () => {
  const dispatch = useAppDispatch()
  const streamState = React.useContext(Stream)
  const {addToast} = useToasts()

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
    }
  }, [streamState.stream])

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
