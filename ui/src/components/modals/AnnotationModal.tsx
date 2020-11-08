import React, {FormEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import clone from 'clone'

import {RootState, useAppDispatch} from '../../store'
import {annotationModalActions, taskActions} from '../../reducers'
import {commitTask} from '../../thunks/tasks'

const AnnotationModal: FunctionComponent = () => {
  const [annotation, setAnnotation] = React.useState('')
  const selectedTask = useSelector(
    (state: RootState) => state.annotationModal.selectedTask
  )
  const dispatch = useAppDispatch()

  function onSaveAnnotation(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    if (!selectedTask) {
      throw Error('No selected task was found')
    }

    const annotations = clone(selectedTask.annotations, false) || []
    annotations.push(annotation)

    dispatch(
      taskActions.updateTask({
        taskId: selectedTask.uuid,
        update: {annotations},
      })
    )
    dispatch(commitTask(selectedTask.uuid))
    dispatch(annotationModalActions.unselectTaskForNewAnnotation())
  }

  function onCancelAnnotation() {
    dispatch(annotationModalActions.unselectTaskForNewAnnotation())
  }

  React.useEffect(() => {
    setAnnotation('')
  }, [selectedTask?.uuid])

  React.useEffect(() => {
    document.getElementById('annotation')?.focus()
  })

  return (
    <>
      {selectedTask && (
        <div className="modal">
          <div className="modal-content">
            <h1>Add Annotation</h1>
            <p className="lead">
              Enter the annotation you'd like to add to "
              {selectedTask.description}"
            </p>
            <form onSubmit={onSaveAnnotation}>
              <textarea
                value={annotation}
                id="annotation"
                onChange={(e) => setAnnotation(e.target.value)}
              />
              <button
                type="button"
                className="button"
                onClick={onCancelAnnotation}
              >
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

export default AnnotationModal
