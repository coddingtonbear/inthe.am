import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit'

import {Task, getTasks} from '../clients/tasks'
import {getAuthenticationToken} from '../reducers/authenticationToken'
import {AppDispatch, RootState} from '../store'

const tasksUpdated = (tasks: Task[], action: PayloadAction<Task[]>): Task[] => {
  return action.payload
}

const initialState = [] as Task[]

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
    const authenticationToken = await thunkAPI.dispatch(getAuthenticationToken)
    if (authenticationToken) {
      const tasks = await getTasks(authenticationToken)
      thunkAPI.dispatch(tasksSlice.actions.tasksUpdated(tasks))
    }
  }
)

export default tasksSlice.reducer
