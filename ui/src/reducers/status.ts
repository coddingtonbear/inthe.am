import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit'

import {Status, getStatus} from '../clients/status'
import {getAuthenticationToken} from '../reducers/authenticationToken'
import {AppDispatch, RootState} from '../store'

const statusUpdated = (
  state: Status,
  action: PayloadAction<Status>
): Status => {
  return action.payload
}

const initialState = {logged_in: false} as Status

const statusSlice = createSlice({
  name: 'status',
  initialState,
  reducers: {
    statusUpdated,
  },
})

export const refreshStatus = createAsyncThunk<
  void,
  undefined,
  {state: RootState; dispatch: AppDispatch}
>(
  'status/refreshStatus',
  async (_, thunkAPI): Promise<void> => {
    const authenticationToken = await thunkAPI.dispatch(getAuthenticationToken)
    if (authenticationToken) {
      const status = await getStatus(authenticationToken)
      thunkAPI.dispatch(statusSlice.actions.statusUpdated(status))
    } else {
    }
  }
)

export default statusSlice.reducer
