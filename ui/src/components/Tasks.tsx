import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'

import {RootState} from '../store'

const Tasks: FunctionComponent = () => {
  const tasks = useSelector((state: RootState) => state.tasks)
  return <div>TASKS</div>
}

export default Tasks
