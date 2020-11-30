import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {useAppDispatch} from '../store'
import {refreshStatus} from '../reducers/status'
import {ToastProvider} from 'react-toast-notifications'
import {HotKeys, HotKeysProps} from 'react-hotkeys'

import AnnotationModal from './modals/AnnotationModal'
import {RootState} from '../store'
import EditTaskModal from './modals/EditTaskModal'
import {createStream} from '../clients/stream'
import {Stream} from '../contexts/stream'
import AppRouter from './AppRouter'

const App: FunctionComponent = () => {
  const loggedIn = useSelector((state: RootState) => state.status.logged_in)
  const head = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.repository_head : null
  )
  const statusUrl = useSelector(
    (state: RootState) => state.status.urls?.status_feed
  )
  const dispatch = useAppDispatch()
  const [stream, setStream] = React.useState<EventSource>()

  const keyMap: HotKeysProps['keyMap'] = {
    NAV_TASK_LIST: 'alt+t',
    NAV_TRELLO: 'alt+k',
    NAV_DOCS: 'alt+h',
    NAV_ACTIVITY_LOG: 'alt+l',
    NAV_CONFIGURE: 'alt+/',

    LOG_OUT: 'alt+x',
    CREATE_TASK: 'alt+n',
    REFERSH_TASKS: 'alt+r',

    TASK_STOP_START: 'alt+s',
    TASK_ADD_ANNOTATION: 'alt+a',
    TASK_EDIT: 'alt+e',
    TASK_COMPLETE: 'alt+c',
    TASK_DELETE: 'alt+d',
  }

  dispatch(refreshStatus)

  React.useEffect(() => {
    if (stream) {
      stream.close()
    }

    if (statusUrl) {
      const newStream = createStream(statusUrl, head)
      setStream(newStream)
    }
  }, [statusUrl])

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
            <Stream.Provider value={{stream}}>
              <HotKeys keyMap={keyMap} className="hotkey-listener">
                <AppRouter />
                <AnnotationModal />
                <EditTaskModal />
              </HotKeys>
            </Stream.Provider>
          </ToastProvider>
        </>
      )}
    </>
  )
}

export default App
