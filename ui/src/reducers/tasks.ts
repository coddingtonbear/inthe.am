import {createSlice, PayloadAction, Slice} from '@reduxjs/toolkit'

import {Task} from '../clients/tasks'

type TaskState = Task[] | null

const tasksUpdated = (
  tasks: TaskState,
  action: PayloadAction<Task[]>
): Task[] => {
  return action.payload
}

const reducers = {tasksUpdated}

export type TaskSlice = Slice<TaskState, typeof reducers, 'tasks'>

const initialState = null as TaskState

const tasksSlice: TaskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: reducers,
})

export default tasksSlice
