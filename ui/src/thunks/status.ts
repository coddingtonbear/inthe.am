import {createAsyncThunk} from '@reduxjs/toolkit'
import {AppDispatch, RootState} from '../store'

import * as client from '../clients/status'
import {statusActions} from '../reducers'

export const refreshStatus = createAsyncThunk<
  void,
  void,
  {state: RootState; dispatch: AppDispatch}
>(
  'status/refreshStatus',
  async (_, thunkAPI): Promise<void> => {
    const status = await client.getStatus()

    thunkAPI.dispatch(statusActions.statusUpdated(status))
  }
)
