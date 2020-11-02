import React, {FunctionComponent} from 'react'
import {Task} from '../clients/tasks'

export interface Props {
  tasks: Task[]
  task: Task
}

const TaskDetails: FunctionComponent<Props> = ({tasks, task}) => {
  return <div id="task-details">{task.uuid} -- OK</div>
}

export default TaskDetails
