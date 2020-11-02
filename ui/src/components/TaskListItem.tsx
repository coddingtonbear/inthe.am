import React, {FunctionComponent} from 'react'
import classnames from 'classnames'
import {DateTime, Duration} from 'luxon'
import {Link} from 'react-router-dom'

import {Task} from '../clients/tasks'

import Icon from './Icon'

export type TaskClass =
  | 'active'
  | 'blocking'
  | 'blocked'
  | 'overdue'
  | 'due__today'
  | 'due'
  | 'recurring'
  | 'pri__H'
  | 'pri__M'
  | 'pri__L'
  | 'tagged'
  | ''

export const taskIsRelevant = (task: Task): boolean => {
  return !['completed', 'deleted'].includes(task.status)
}

export const taskIsBlocking = (tasks: Task[], task: Task): boolean => {
  const blockedTasks = tasks.filter(
    (otherTask) => task.blocks && task.blocks.includes(otherTask.uuid)
  )
  for (const otherTask of blockedTasks) {
    if (taskIsRelevant(otherTask)) {
      return true
    }
  }
  return false
}

export const taskIsBlocked = (tasks: Task[], task: Task): boolean => {
  for (const otherTask of tasks) {
    if (
      otherTask.blocks &&
      otherTask.blocks.includes(task.uuid) &&
      taskIsRelevant(otherTask)
    ) {
      return true
    }
  }
  return false
}

export const getTaskwarriorClass = (tasks: Task[], task: Task): TaskClass => {
  if (task.start) {
    return 'active'
  } else if (taskIsBlocking(tasks, task)) {
    return 'blocking'
  } else if (taskIsBlocked(tasks, task)) {
    return 'blocked'
  } else if (task.due && DateTime.fromISO(task.due) < DateTime.local()) {
    return 'overdue'
  } else if (
    task.due &&
    DateTime.fromISO(task.due).hasSame(DateTime.local(), 'day')
  ) {
    return 'due__today'
  } else if (
    task.due &&
    DateTime.fromISO(task.due) <
      DateTime.local().plus(Duration.fromObject({days: 7}))
  ) {
    return 'due'
  } else if (task.imask) {
    return 'recurring'
  } else if (task.priority === 'H') {
    return 'pri__H'
  } else if (task.priority === 'M') {
    return 'pri__M'
  } else if (task.priority === 'L') {
    return 'pri__L'
  } else if (task.tags && task.tags.length) {
    return 'tagged'
  }

  return ''
}

export const getTaskIcon = (task: Task): string => {
  if (task.status === 'completed') {
    return 'check'
  } else if (task.start) {
    return 'asterisk'
  } else if (task.due) {
    return 'clock'
  } else {
    return 'target'
  }
}

export interface Props {
  tasks: Task[]
  task: Task
}

const TaskListItem: FunctionComponent<Props> = ({tasks, task}) => {
  return (
    <Link to={`/tasks/${task.uuid}`}>
      <div className="task">
        <div
          className={classnames('task-item', getTaskwarriorClass(tasks, task))}
        >
          <div className={classnames('task-list-icon', task.status)}>
            <Icon name={getTaskIcon(task)} />
          </div>
          <div className="task-list-item">
            {task.project && (
              <h5 className="status" title={task.project}>
                {task.project}
              </h5>
            )}
            <p className="description">{task.description}</p>
            <p className="tags">
              {task.annotations && <Icon name="page-edit" />}
              {task.tags &&
                task.tags.map((tag) => {
                  return (
                    <React.Fragment key={tag}>
                      <Icon name="price-tag" />
                      {tag}
                    </React.Fragment>
                  )
                })}
            </p>
            <p className="duedatetime">
              {task.due && (
                <>
                  <Icon name="clock" />
                  {DateTime.fromISO(task.due).toRelative()}
                </>
              )}
            </p>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default TaskListItem
