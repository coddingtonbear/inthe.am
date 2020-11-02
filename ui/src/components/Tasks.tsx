import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'

import {RootState, useAppDispatch} from '../store'
import {refreshTasks} from '../reducers/tasks'
import TaskListItem from './TaskListItem'

const Tasks: FunctionComponent = () => {
  const tasks = useSelector((state: RootState) => state.tasks)
  const dispatch = useAppDispatch()
  const stylesheet = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.colorscheme : null
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
    <div className="row full-width">
      <div id="list" className="task-list">
        {tasks.map((task) => (
          <TaskListItem tasks={tasks} task={task} key={task.id} />
        ))}
      </div>
    </div>
  )
}

export default Tasks
