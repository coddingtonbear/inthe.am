import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RouteComponentProps} from 'react-router'

import {RootState, useAppDispatch} from '../store'
import {refreshTask, refreshTasks} from '../thunks/tasks'
import TaskListItem from './TaskListItem'
import TaskDetails from './TaskDetails'
import {Stream} from '../contexts/stream'
import {getMessage, StreamEventType} from '../clients/stream'

interface MatchParams {
  taskId: string
}

interface Props extends RouteComponentProps<MatchParams> {}

const Tasks: FunctionComponent<Props> = ({match, ...rest}) => {
  const tasks = useSelector((state: RootState) => state.tasks)
  const selectedTaskId = match.params.taskId
  const task = match
    ? tasks?.filter((task) => task.uuid === selectedTaskId)[0]
    : null
  const dispatch = useAppDispatch()
  const stylesheet = useSelector((state: RootState) =>
    state.status.logged_in === true ? state.status.colorscheme : null
  )
  const streamState = React.useContext(Stream)

  React.useEffect(() => {
    if (streamState.stream) {
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
    dispatch(refreshTasks())
  }, [])

  return (
    <>
      <div className="row full-width">
        <div id="list" className="task-list">
          {tasks &&
            tasks.map((task) => (
              <TaskListItem
                tasks={tasks}
                task={task}
                key={task.id}
                active={task.id === selectedTaskId}
              />
            ))}
        </div>
        {task && tasks && <TaskDetails tasks={tasks} task={task} />}
      </div>
    </>
  )
}

export default Tasks
