import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {useAppDispatch} from '../store'
import {refreshStatus} from '../reducers/status'
import {ToastProvider} from 'react-toast-notifications'

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
              <AppRouter />
              <AnnotationModal />
              <EditTaskModal />
            </Stream.Provider>
          </ToastProvider>
        </>
      )}
    </>
  )
}

export default App
