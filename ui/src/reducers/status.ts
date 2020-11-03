import {createSlice, PayloadAction} from '@reduxjs/toolkit'
import {useSelector} from 'react-redux'

import {Status, URLList, getStatus} from '../clients/status'
import {AppDispatch, RootState} from '../store'

const statusUpdated = (
  state: Status,
  action: PayloadAction<Status>
): Status => {
  return action.payload
}

const initialState = {logged_in: null} as Status

const statusSlice = createSlice({
  name: 'status',
  initialState,
  reducers: {
    statusUpdated,
  },
})

export const refreshStatus = async (
  dispatch: AppDispatch,
  getState: () => RootState
): Promise<void> => {
  const status = await getStatus()
  dispatch(statusSlice.actions.statusUpdated(status))
}

export default statusSlice

export const useUrls = (): URLList | undefined =>
  useSelector<RootState, URLList | undefined>((s) => {
    return s.status.urls
  })
