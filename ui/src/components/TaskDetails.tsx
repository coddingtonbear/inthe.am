import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {DateTime} from 'luxon'

import {Task} from '../clients/tasks'
import Icon from './Icon'
import {taskIsEditable, getBlockedTasks, getBlockingTasks} from '../utils/task'
import {RootState} from '../store'

export interface Props {
  tasks: Task[]
  task: Task
}

const TaskDetails: FunctionComponent<Props> = ({tasks, task}) => {
  const udas = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.udas : null
  )

  const [blocking, setBlocking] = React.useState<Task[]>([])
  const [blocked, setBlocked] = React.useState<Task[]>([])

  React.useEffect(() => {
    setBlocking(getBlockingTasks(tasks, task))
    setBlocked(getBlockedTasks(tasks, task))
  }, [JSON.stringify(tasks), task.uuid])

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
              <i className="fa fa-clock-o">
                {DateTime.fromISO(task.due).toRelative()}
              </i>
            )}

            {task.tags?.map((tag) => {
              return (
                <>
                  <Icon name="price-tag" />
                  {tag}
                </>
              )
            })}
          </div>
        </div>
      </div>
      <div className="row" id="task-action-bar">
        <div className="medium-12">
          {taskIsEditable(task) && (
            <ul id="task-actions" className="inline-list">
              {task.start && (
                <li data-intro="alt+s">
                  <a>
                    <i className="fa fa-star-o">Stop</i>
                  </a>
                </li>
              )}
              {!task.start && (
                <li data-intro="alt+s">
                  <a>
                    <i className="fa fa-star">Start</i>
                  </a>
                </li>
              )}
              <li data-intro="alt+a">
                <a>
                  <i className="fa fa-pencil">Add Annotation</i>
                </a>
              </li>
              <li data-intro="alt+e">
                <a>
                  <i className="fa fa-pencil-square-o">Edit</i>
                </a>
              </li>
              <li data-intro="alt+c">
                <a>
                  <i className="fa fa-check-circle-o">Mark Completed</i>
                </a>
              </li>
              <li data-intro="alt+d">
                <a>
                  <i className="fa fa-ban">Delete</i>
                </a>
              </li>
            </ul>
          )}
        </div>
      </div>
      <div className="row task-content-body">
        <div className="medium-6 columns details_table">
          <table className="details">
            <tbody>
              {blocking && (
                <tr>
                  <th>Depends Upon</th>
                  <td>
                    <ul className="depends_tickets">
                      {blocking.map((blocking) => (
                        <li className={blocking.status}>
                          {blocking.description}
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              )}
              {blocked && (
                <tr>
                  <th>Blocks</th>
                  <td>
                    <ul className="blocked_tickets">
                      {blocked.map((blocked) => (
                        <li className={blocked.status}>
                          {blocked.description}
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
                    <>
                      <Icon name="price-tag" />
                      {tag}
                    </>
                  ))}
                </td>
              </tr>
              <tr>
                <th>Urgency</th>
                <td>{task.urgency}</td>
              </tr>
              <tr>
                <th>Priority</th>
                <td>{task.priority}</td>
              </tr>
              <tr>
                <th>Due</th>
                <td>{task.due}</td>
              </tr>
              <tr>
                <th>Entered</th>
                <td>{task.entry}</td>
              </tr>
              <tr>
                <th>Started</th>
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
                {
                  task.udas[uda.field] && (
                    <tr>
                      <th>{uda.label}</th>
                      <td>{task.udas[uda.field]}</td>
                    </tr>
                  )
                }
              })}
            </tbody>
          </table>
        </div>
        <div className="medium-6 columns annotations_list">
          <ul className="annotation_list">
            {task.annotations?.map((annotation) => {
              return (
                <li>
                  <span className="annotation_tools">
                    <a className="delete-annotation-link">&#215;</a>
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
