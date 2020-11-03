import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit'

import {Task, getTasks} from '../clients/tasks'
import {AppDispatch, RootState} from '../store'

const tasksUpdated = (
  tasks: Task[] | null,
  action: PayloadAction<Task[]>
): Task[] => {
  return action.payload
}

const initialState = null as Task[] | null

const tasksSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    tasksUpdated,
  },
})

export const refreshTasks = createAsyncThunk<
  void,
  undefined,
  {state: RootState; dispatch: AppDispatch}
>(
  'tasks/refreshTasks',
  async (_, thunkAPI): Promise<void> => {
    const tasks = await getTasks()
    thunkAPI.dispatch(tasksSlice.actions.tasksUpdated(tasks))
  }
)

export default tasksSlice.reducer
