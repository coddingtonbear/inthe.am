import {createAsyncThunk} from '@reduxjs/toolkit'
import {AppDispatch, RootState} from '../store'

import * as client from '../clients/tasks'
import {taskActions} from '../reducers'

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
    return await client.stopTask(taskId)
  }
)

export const startTask = createAsyncThunk<
  void,
  client.UUID,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/startTask',
  async (taskId, thunkAPI): Promise<void> => {
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
    return await client.completeTask(taskId)
  }
)
