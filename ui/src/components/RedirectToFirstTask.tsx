import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Redirect} from 'react-router'

import {RootState, useAppDispatch} from '../store'
import {refreshTasks} from '../thunks/tasks'

const RedirectToFirstTask: FunctionComponent = () => {
  const tasks = useSelector((state: RootState) => state.tasks)
  const dispatch = useAppDispatch()

  React.useEffect(() => {
    if (tasks === null) {
      dispatch(refreshTasks())
    }
  }, [])

  return (
    <>
      {tasks && tasks.length > 0 && <Redirect to={`/tasks/${tasks[0].uuid}`} />}
      {tasks && tasks.length === 0 && <Redirect to={`/getting-started`} />}
      {!tasks && <></>}
    </>
  )
}

export default RedirectToFirstTask
