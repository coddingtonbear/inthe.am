import React, {FunctionComponent} from 'react'
import classnames from 'classnames'
import {DateTime, Duration} from 'luxon'
import {Link} from 'react-router-dom'

import {taskIsBlocked, taskIsBlocking} from '../utils/task'
import {Task} from '../clients/tasks'

import Icon from './Icon'
import LabeledIcon from './LabeledIcon'
import Tag from './Tag'

export type TaskClass =
  | 'active'
  | 'blocking'
  | 'blocked'
  | 'overdue'
  | 'due__today'
  | 'due'
  | 'recurring'
  | 'tagged'
  | ''

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
  active: boolean
}

const TaskListItem: FunctionComponent<Props> = ({tasks, task, active}) => {
  return (
    <Link to={`/tasks/${task.uuid}`}>
      <div className={classnames('task', {active: active})}>
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
              {task.annotations && <Icon name="comment" />}
              {task.tags &&
                task.tags.map((tag) => {
                  return <Tag key={tag} name={tag} />
                })}
            </p>
            <p className="duedatetime">
              {task.due && (
                <>
                  <LabeledIcon
                    icon="clock"
                    label={DateTime.fromISO(task.due).toRelative() ?? ''}
                  />
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
