import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RouteComponentProps} from 'react-router'

import {RootState, useAppDispatch} from '../store'
import {refreshTasks} from '../reducers/tasks'
import TaskListItem from './TaskListItem'
import TaskDetails from './TaskDetails'

interface MatchParams {
  taskId: string
}

interface Props extends RouteComponentProps<MatchParams> {}

const Tasks: FunctionComponent<Props> = ({match, ...rest}) => {
  const tasks = useSelector((state: RootState) => state.tasks)
  const task = match
    ? tasks?.filter((task) => task.uuid === match.params.taskId)[0]
    : null
  const dispatch = useAppDispatch()
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
    dispatch(refreshTasks())
  }, [])

  return (
    <>
      <div className="row full-width">
        <div id="list" className="task-list">
          {tasks &&
            tasks.map((task) => (
              <TaskListItem tasks={tasks} task={task} key={task.id} />
            ))}
        </div>
        {task && tasks && <TaskDetails tasks={tasks} task={task} />}
      </div>
    </>
  )
}

export default Tasks
