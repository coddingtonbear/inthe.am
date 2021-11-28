import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {DateTime} from 'luxon'
import clone from 'clone'

import {Task} from '../clients/tasks'
import {Change, getTaskChanges} from '../clients/changes'
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
import Footer from './Footer'
import {HotKeys, HotKeysProps} from 'react-hotkeys'
import Icon from './Icon'

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

  const [changesShown, setChangesShown] = React.useState<boolean>(false)
  const [changes, setChanges] = React.useState<Change[]>([])

  const keyMapHandlers: HotKeysProps['handlers'] = {
    TASK_STOP_START: () => {
      if (task.start) {
        onStopTask()
      } else {
        onStartTask()
      }
    },
    TASK_EDIT: onEditTask,
    TASK_ADD_ANNOTATION: onAddAnnotation,
    TASK_COMPLETE: onCompleteTask,
    TASK_DELETE: onDeleteTask,
  }

  React.useEffect(() => {
    setBlocking(getBlockingTasks(tasks, task))
    setBlocked(getBlockedTasks(tasks, task))
  }, [JSON.stringify(tasks), task.uuid])

  React.useEffect(() => {
    if (changesShown) {
      // This fires before the actual request is completed; this is
      // kind of a cludge, but it'll at least make recent changes appear.
      setTimeout(onRefreshChanges, 5000)
    }
  }, [JSON.stringify(task), changesShown])

  function onAddAnnotation() {
    dispatch(annotationModalActions.selectTaskForNewAnnotation(task))
  }

  async function onEditTask() {
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

  function onRefreshChanges() {
    setChanges([])
    getTaskChanges(task.uuid).then((changes) => {
      setChanges(changes)
      setChangesShown(true)
    })
  }

  return (
    <HotKeys handlers={keyMapHandlers} allowChanges={true} id="task-details">
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
              <tr>
                <th>Changes</th>
                <td>
                  <div className="medium-6 columns change_list">
                    {changesShown ? (
                      <>
                        {changes.length > 0 && (
                          <>
                            <table>
                              <thead>
                                <tr>
                                  <th>Date</th>
                                  <th>Field</th>
                                  <th>From</th>
                                  <th>To</th>
                                  <th>Source Type</th>
                                  <th>Source ID</th>
                                </tr>
                              </thead>
                              <tbody>
                                {changes.map((change) => {
                                  return (
                                    <tr key={change.id}>
                                      <td>{change.changed}</td>
                                      <td>{change.field}</td>
                                      <td>{change.data_from}</td>
                                      <td>{change.data_to}</td>
                                      <td>{change.source.sourcetype_name}</td>
                                      <td>{change.source.id}</td>
                                    </tr>
                                  )
                                })}
                              </tbody>
                            </table>
                          </>
                        )}
                        <a onClick={() => onRefreshChanges()}>
                          <Icon name="refresh" />
                        </a>
                      </>
                    ) : (
                      <>
                        <a onClick={() => onRefreshChanges()}>Show changes</a>
                      </>
                    )}
                  </div>
                </td>
              </tr>
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
      <Footer />
    </HotKeys>
  )
}

export default TaskDetails
