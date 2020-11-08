import {createSlice, PayloadAction, Slice} from '@reduxjs/toolkit'

import {TaskUpdate} from '../clients/tasks'

export interface EditTaskModalState {
  selectedTask?: TaskUpdate
}

const selectTaskForEdit = (
  state: EditTaskModalState,
  action: PayloadAction<TaskUpdate | null>
): void => {
  state.selectedTask = action.payload ?? {}
}

const unselectTaskForEdit = (
  state: EditTaskModalState,
  action: PayloadAction<void>
): EditTaskModalState => {
  return {}
}

const reducers = {
  selectTaskForEdit,
  unselectTaskForEdit,
}

export type EditTaskModalSlice = Slice<
  EditTaskModalState,
  typeof reducers,
  'editTaskModal'
>

const initialState: EditTaskModalState = {}

const editTaskModalSlice: EditTaskModalSlice = createSlice({
  name: 'editTaskModal',
  initialState,
  reducers: reducers,
})

export default editTaskModalSlice
