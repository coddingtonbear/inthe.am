import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RouteComponentProps} from 'react-router'

import {RootState} from '../store'
import TaskDetails from './TaskDetails'
import FilterableTaskList from './FilterableTaskList'

interface MatchParams {
  taskId: string | undefined
}

interface Props extends RouteComponentProps<MatchParams> {}

const MobileTasks: FunctionComponent<Props> = ({match, ...rest}) => {
  const tasks = useSelector((state: RootState) => state.tasks)
  const selectedTaskId = match.params.taskId
  const task = match
    ? tasks?.filter((task) => task.uuid === selectedTaskId)[0]
    : null

  return (
    <>
      <div className="row full-width">
        <FilterableTaskList
          tasks={tasks}
          selectedTask={task ?? null}
          mode="mobile"
        />
      </div>
    </>
  )
}

export default MobileTasks
