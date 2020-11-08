import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {GridContainer, Grid, Cell} from 'react-foundation'

import {RootState, useAppDispatch} from '../../store'
import {taskActions, editTaskModalActions} from '../../reducers'
import {commitTask, createTask} from '../../thunks/tasks'
import {TaskUpdate} from '../../clients/tasks'

const EditTaskModal: FunctionComponent = () => {
  const selectedTask = useSelector(
    (state: RootState) => state.editTaskModal.selectedTask
  )

  const [description, setDescription] = React.useState<string>('')
  const [project, setProject] = React.useState<string>('')
  const [tags, setTags] = React.useState<string[]>([])
  const [due, setDue] = React.useState<string | undefined>(undefined)
  const [wait, setWait] = React.useState<string | undefined>(undefined)
  const [scheduled, setScheduled] = React.useState<string | undefined>(
    undefined
  )

  React.useEffect(() => {
    setDescription(selectedTask?.description ?? '')
    setProject(selectedTask?.project ?? '')
    setTags(selectedTask?.tags ?? [])
    setDue(selectedTask?.due ?? undefined)
    setWait(selectedTask?.wait ?? undefined)
    setScheduled(selectedTask?.scheduled ?? undefined)
  }, [JSON.stringify(selectedTask)])

  const dispatch = useAppDispatch()

  function onSaveTask() {
    if (!selectedTask) {
      throw Error('No selected task was found')
    }

    const partialTask: TaskUpdate = {
      description,
      project,
      tags,
      due,
      wait,
      scheduled,
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

  return (
    <>
      {selectedTask && (
        <div className="modal">
          <div className="modal-content grid-container">
            {selectedTask.uuid && <h1>Change your task</h1>}
            {!selectedTask.uuid && <h1>Create a new task</h1>}

            <Grid>
              <Cell medium={12}>
                <label>
                  Description
                  <input
                    type="text"
                    value={description}
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

            <button type="button" className="button" onClick={onCancelEdit}>
              Cancel
            </button>
            <button
              type="button"
              className="success button"
              onClick={onSaveTask}
            >
              Save
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default EditTaskModal
