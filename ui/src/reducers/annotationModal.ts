import {createSlice, PayloadAction, Slice} from '@reduxjs/toolkit'

import {Task} from '../clients/tasks'

export interface AnnotationModalState {
  selectedTask?: Task
}

const selectTaskForNewAnnotation = (
  state: AnnotationModalState,
  action: PayloadAction<Task>
): void => {
  state.selectedTask = action.payload
}

const unselectTaskForNewAnnotation = (
  state: AnnotationModalState,
  action: PayloadAction<void>
): AnnotationModalState => {
  return {}
}

const reducers = {
  selectTaskForNewAnnotation,
  unselectTaskForNewAnnotation,
}

export type AnnotationModalSlice = Slice<
  AnnotationModalState,
  typeof reducers,
  'annotation_modal'
>

const initialState: AnnotationModalState = {}

const annotationModalSlice: AnnotationModalSlice = createSlice({
  name: 'annotation_modal',
  initialState,
  reducers: reducers,
})

export default annotationModalSlice
