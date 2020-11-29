import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {DateTime} from 'luxon'
import clone from 'clone'

import {Task} from '../clients/tasks'
import LabeledIcon from './LabeledIcon'
import {taskIsEditable, getBlockedTasks, getBlockingTasks} from '../utils/task'
import {
  stopTask,
  startTask,
  completeTask,
  deleteTask,
  commitTask,
} from '../thunks/tasks'
import {RootState, useAppDispatch} from '../store'
import {
  annotationModalActions,
  editTaskModalActions,
  taskActions,
} from '../reducers'
import Tag from './Tag'

export interface Props {
  tasks: Task[]
  task: Task
}

const TaskDetails: FunctionComponent<Props> = ({tasks, task}) => {
  const dispatch = useAppDispatch()
  const udas = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.udas : null
  )

  const [blocking, setBlocking] = React.useState<Task[]>([])
  const [blocked, setBlocked] = React.useState<Task[]>([])

  React.useEffect(() => {
    setBlocking(getBlockingTasks(tasks, task))
    setBlocked(getBlockedTasks(tasks, task))
  }, [JSON.stringify(tasks), task.uuid])

  function onAddAnnotation() {
    dispatch(annotationModalActions.selectTaskForNewAnnotation(task))
  }

  function onEditTask() {
    dispatch(editTaskModalActions.selectTaskForEdit(task))
  }

  function onDeleteAnotation(idx: number) {
    const annotations = clone(task.annotations, false) || []
    annotations.splice(idx, 1)

    dispatch(
      taskActions.updateTask({
        taskId: task.uuid,
        update: {
          annotations: annotations,
        },
      })
    )
    dispatch(commitTask(task.uuid))
  }

  function onStartTask() {
    dispatch(startTask(task.uuid))
  }

  function onStopTask() {
    dispatch(stopTask(task.uuid))
  }

  function onCompleteTask() {
    dispatch(completeTask(task.uuid))
  }

  function onDeleteTask() {
    dispatch(deleteTask(task.uuid))
  }

  return (
    <div id="task-details">
      <div className="row" id="task-header">
        <div className="medium-12">
          <h1 className="title">{task.description}</h1>
          {task.project && (
            <p className="subtitle" title={task.project}>
              <span className="project">{task.project}</span>
            </p>
          )}
          <div className="tags">
            {task.due && (
              <LabeledIcon
                icon="clock"
                label={DateTime.fromISO(task.due).toRelative() ?? ''}
              />
            )}

            {task.tags?.map((tag) => {
              return <Tag name={tag} key={tag} />
            })}
          </div>
        </div>
      </div>
      <div className="row" id="task-action-bar">
        <div className="medium-12">
          {taskIsEditable(task) && (
            <ul id="task-actions" className="inline-list">
              {task.start && (
                <li onClick={onStopTask}>
                  <LabeledIcon icon="stop" label="Stop" />
                </li>
              )}
              {!task.start && (
                <li onClick={onStartTask}>
                  <LabeledIcon icon="play" label="Start" />
                </li>
              )}
              <li onClick={onAddAnnotation}>
                <LabeledIcon icon="comment" label="Add Annotation" />
              </li>
              <li onClick={onEditTask}>
                <LabeledIcon icon="pencil" label="Edit" />
              </li>
              <li onClick={onCompleteTask}>
                <LabeledIcon icon="check" label="Mark Completed" />
              </li>
              <li onClick={onDeleteTask}>
                <LabeledIcon icon="x" label="Delete" />
              </li>
            </ul>
          )}
        </div>
      </div>
      <div className="row task-content-body">
        <div className="medium-6 columns details_table">
          <table className="details">
            <tbody>
              {blocking.length > 0 && (
                <tr>
                  <th>Depends Upon</th>
                  <td>
                    <ul className="depends_tickets">
                      {blocking.map((blocking_task) => (
                        <li
                          className={blocking_task.status}
                          key={blocking_task.uuid}
                        >
                          {blocking_task.description}
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              )}
              {blocked.length > 0 && (
                <tr>
                  <th>Blocks</th>
                  <td>
                    <ul className="blocked_tickets">
                      {blocked.map((blocked_task) => (
                        <li
                          className={blocked_task.status}
                          key={blocked_task.uuid}
                        >
                          {blocked_task.description}
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              )}
              <tr>
                <th>Description</th>
                <td>{task.description}</td>
              </tr>
              <tr>
                <th>Project</th>
                <td>
                  <span className="project">{task.project}</span>
                </td>
              </tr>
              <tr>
                <th>Status</th>
                <td>{task.status}</td>
              </tr>
              <tr>
                <th>Tags</th>
                <td>
                  {task.tags?.map((tag) => (
                    <Tag key={tag} name={tag} />
                  ))}
                </td>
              </tr>
              <tr>
                <th>Urgency</th>
                <td>{task.urgency}</td>
              </tr>
              <tr>
                <th>Due</th>
                <td>{task.due}</td>
              </tr>
              <tr>
                <th>Entry</th>
                <td>{task.entry}</td>
              </tr>
              <tr>
                <th>Start</th>
                <td>{task.start}</td>
              </tr>
              <tr>
                <th>Wait</th>
                <td>{task.wait}</td>
              </tr>
              <tr>
                <th>Scheduled</th>
                <td>{task.scheduled}</td>
              </tr>
              <tr>
                <th>Modified</th>
                <td>{task.modified}</td>
              </tr>
              <tr>
                <th>UUID</th>
                <td>
                  <span className="uuid">{task.uuid}</span>
                </td>
              </tr>
              {udas?.map((uda) => {
                return (
                  task.udas[uda.field] && (
                    <tr key={uda.field + task.udas[uda.field]}>
                      <th>{uda.label}</th>
                      <td>{task.udas[uda.field]}</td>
                    </tr>
                  )
                )
              })}
            </tbody>
          </table>
        </div>
        <div className="medium-6 columns annotations_list">
          <ul className="annotation_list">
            {task.annotations?.map((annotation, idx) => {
              return (
                <li key={annotation}>
                  <span className="annotation_tools">
                    <a
                      className="delete-annotation-link"
                      onClick={() => onDeleteAnotation(idx)}
                    >
                      &#215;
                    </a>
                  </span>
                  {annotation}
                </li>
              )
            })}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default TaskDetails
