import {createAsyncThunk} from '@reduxjs/toolkit'
import {AppDispatch, RootState} from '../store'
import {push} from 'connected-react-router'

import * as client from '../clients/tasks'
import {taskActions} from '../reducers'
import {currentTimestamp} from '../utils/task'

export const refreshTasks = createAsyncThunk<
  void,
  undefined,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/refreshTasks',
  async (_, thunkAPI): Promise<void> => {
    const tasks = await client.getTasks()
    thunkAPI.dispatch(taskActions.tasksUpdated(tasks))
  }
)

export const stopTask = createAsyncThunk<
  void,
  client.UUID,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/stopTask',
  async (taskId, thunkAPI): Promise<void> => {
    thunkAPI.dispatch(
      taskActions.updateTask({
        taskId,
        update: {
          start: '',
          end: currentTimestamp(),
        },
      })
    )
    return await client.stopTask(taskId)
  }
)

export const deleteTask = createAsyncThunk<
  void,
  client.UUID,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/deleteTask',
  async (taskId, thunkAPI): Promise<void> => {
    thunkAPI.dispatch(taskActions.removeTask(taskId))
    return await client.deleteTask(taskId)
  }
)

export const startTask = createAsyncThunk<
  void,
  client.UUID,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/startTask',
  async (taskId, thunkAPI): Promise<void> => {
    thunkAPI.dispatch(
      taskActions.updateTask({
        taskId,
        update: {
          start: currentTimestamp(),
        },
      })
    )
    return await client.startTask(taskId)
  }
)

export const completeTask = createAsyncThunk<
  void,
  client.UUID,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/completeTask',
  async (taskId, thunkAPI): Promise<void> => {
    thunkAPI.dispatch(
      taskActions.updateTask({
        taskId,
        update: {
          status: 'completed',
        },
      })
    )
    const result = await client.completeTask(taskId)

    setTimeout(() => thunkAPI.dispatch(taskActions.removeTask(taskId)), 3000)

    return result
  }
)

export const commitTask = createAsyncThunk<
  void,
  client.UUID,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/commitTask',
  async (taskId, thunkAPI): Promise<void> => {
    const taskState = thunkAPI.getState()
    const thisTask = taskState.tasks?.find((task) => task.uuid === taskId)

    if (!thisTask) {
      throw Error(`Could not find task by ID ${taskId}`)
    }

    return await client.updateTask(thisTask)
  }
)

export const createTask = createAsyncThunk<
  void,
  client.TaskUpdate,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/createTask',
  async (partialTask, thunkAPI): Promise<void> => {
    const task = await client.createTask(partialTask)
    thunkAPI.dispatch(taskActions.addTask(task))
    thunkAPI.dispatch(push(`tasks/${task.uuid}`))
  }
)
