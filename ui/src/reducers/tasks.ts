import {createSlice, PayloadAction, Slice} from '@reduxjs/toolkit'

import {Task, TaskUpdate, UUID} from '../clients/tasks'

type TaskState = Task[] | null

const tasksUpdated = (
  tasks: TaskState,
  action: PayloadAction<Task[]>
): Task[] => {
  return action.payload
}

export interface UpdateTaskRequest {
  taskId: UUID
  update: TaskUpdate
}

const updateTask = (
  tasks: TaskState,
  action: PayloadAction<UpdateTaskRequest>
): void => {
  if (!tasks) {
    return
  }

  const updatedTask = action.payload.update
  const existingTaskIndex = tasks.findIndex(
    (task) => task.uuid === action.payload.taskId
  )

  if (existingTaskIndex === -1) {
    throw Error(`Could not find matching task for ${action.payload.taskId}`)
  }

  const existingTask = tasks[existingTaskIndex]

  const task: Task = {
    ...existingTask,
    ...updatedTask,
  }

  tasks[existingTaskIndex] = task
}

const reducers = {tasksUpdated, updateTask}

export type TaskSlice = Slice<TaskState, typeof reducers, 'tasks'>

const initialState = null as TaskState

const tasksSlice: TaskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: reducers,
})

export default tasksSlice
