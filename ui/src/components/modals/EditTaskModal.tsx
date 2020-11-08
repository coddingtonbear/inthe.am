import React, {FormEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Grid, Cell} from 'react-foundation'
import DatePicker from 'react-datepicker'
import {DateTime} from 'luxon'

import {RootState, useAppDispatch} from '../../store'
import {taskActions, editTaskModalActions} from '../../reducers'
import {commitTask, createTask} from '../../thunks/tasks'
import {TaskUpdate} from '../../clients/tasks'

import 'react-datepicker/dist/react-datepicker.css'

const EditTaskModal: FunctionComponent = () => {
  const selectedTask = useSelector(
    (state: RootState) => state.editTaskModal.selectedTask
  )

  const [description, setDescription] = React.useState<string>('')
  const [project, setProject] = React.useState<string>('')
  const [tags, setTags] = React.useState<string[]>([])
  const [due, setDue] = React.useState<Date | undefined>(undefined)
  const [wait, setWait] = React.useState<Date | undefined>(undefined)
  const [scheduled, setScheduled] = React.useState<Date | undefined>(undefined)

  React.useEffect(() => {
    setDescription(selectedTask?.description ?? '')
    setProject(selectedTask?.project ?? '')
    setTags(selectedTask?.tags ?? [])
    setDue(undefined)
    setWait(undefined)
    setScheduled(undefined)
    if (selectedTask?.due) {
      setDue(DateTime.fromISO(selectedTask.due).toJSDate())
    }
    if (selectedTask?.wait) {
      setWait(DateTime.fromISO(selectedTask.wait).toJSDate())
    }
    if (selectedTask?.scheduled) {
      setScheduled(DateTime.fromISO(selectedTask.scheduled).toJSDate())
    }
  }, [JSON.stringify(selectedTask)])

  React.useEffect(() => {
    document.getElementById('edit-task-description')?.focus()
  })

  const dispatch = useAppDispatch()

  function onSaveTask(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    if (!selectedTask) {
      throw Error('No selected task was found')
    }

    const partialTask: TaskUpdate = {
      description,
      project,
      tags,
    }
    if (due) {
      partialTask.due = DateTime.fromJSDate(due).toISO()
    }
    if (wait) {
      partialTask.wait = DateTime.fromJSDate(wait).toISO()
    }
    if (scheduled) {
      partialTask.scheduled = DateTime.fromJSDate(scheduled).toISO()
    }

    if (selectedTask.uuid) {
      dispatch(
        taskActions.updateTask({
          taskId: selectedTask.uuid,
          update: partialTask,
        })
      )
      dispatch(commitTask(selectedTask.uuid))
    } else {
      dispatch(createTask(partialTask))
    }
    dispatch(editTaskModalActions.unselectTaskForEdit())
  }

  function onCancelEdit() {
    dispatch(editTaskModalActions.unselectTaskForEdit())
  }

  function getSingleDateOrUndefined(
    maybeDate: Date | [Date, Date] | null
  ): Date | undefined {
    if (maybeDate instanceof Date) {
      return maybeDate
    }
    if (Array.isArray(maybeDate)) {
      return maybeDate[0]
    }
    return undefined
  }

  return (
    <>
      {selectedTask && (
        <div className="modal">
          <div className="modal-content grid-container">
            {selectedTask.uuid && <h1>Change your task</h1>}
            {!selectedTask.uuid && <h1>Create a new task</h1>}

            <form onSubmit={onSaveTask}>
              <Grid>
                <Cell medium={12}>
                  <label>
                    Description
                    <input
                      type="text"
                      value={description}
                      id="edit-task-description"
                      onChange={(e) => setDescription(e.target.value)}
                    />
                  </label>
                </Cell>
              </Grid>
              <Grid>
                <Cell medium={4}>
                  <label>
                    Project
                    <input
                      type="text"
                      value={project}
                      onChange={(e) => setProject(e.target.value)}
                    />
                  </label>
                </Cell>
                <Cell medium={8}>
                  <label>
                    Tags
                    <input
                      type="text"
                      value={tags.join(' ')}
                      placeholder="tag1 tag2 tag3"
                      onChange={(e) => setTags(e.target.value.split(' '))}
                    />
                  </label>
                </Cell>
              </Grid>
              <Grid>
                <Cell medium={4}>
                  <label>
                    Due
                    <DatePicker
                      selected={due}
                      showTimeSelect={true}
                      onChange={(date) =>
                        setDue(getSingleDateOrUndefined(date))
                      }
                    />
                  </label>
                </Cell>
                <Cell medium={4}>
                  <label>
                    Wait
                    <DatePicker
                      selected={wait}
                      showTimeSelect={true}
                      onChange={(date) =>
                        setWait(getSingleDateOrUndefined(date))
                      }
                    />
                  </label>
                </Cell>
                <Cell medium={4}>
                  <label>
                    Scheduled
                    <DatePicker
                      selected={scheduled}
                      showTimeSelect={true}
                      onChange={(date) =>
                        setScheduled(getSingleDateOrUndefined(date))
                      }
                    />
                  </label>
                </Cell>
              </Grid>

              <button type="button" className="button" onClick={onCancelEdit}>
                Cancel
              </button>
              <button type="submit" className="success button">
                Save
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  )
}

export default EditTaskModal
