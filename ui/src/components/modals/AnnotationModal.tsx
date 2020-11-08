import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RootState, useAppDispatch} from '../../store'
import {annotationModalActions, taskActions} from '../../reducers'
import {commitTask} from '../../thunks/tasks'

const AnnotationModal: FunctionComponent = () => {
  const [annotation, setAnnotation] = React.useState('')
  const selectedTask = useSelector(
    (state: RootState) => state.annotationModal.selectedTask
  )
  const dispatch = useAppDispatch()

  function onSaveAnnotation() {
    if (!selectedTask) {
      throw Error('No selected task was found')
    }

    const annotations = selectedTask.annotations || []
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
            <textarea
              value={annotation}
              onChange={(e) => setAnnotation(e.target.value)}
            />
            <button
              type="button"
              className="button"
              onClick={onCancelAnnotation}
            >
              Cancel
            </button>
            <button
              type="button"
              className="success button"
              onClick={onSaveAnnotation}
            >
              Save
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default AnnotationModal
