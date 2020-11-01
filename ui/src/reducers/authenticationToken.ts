import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit'
import {AppDispatch, RootState} from '../store'
import {retrieveAuthenticationToken} from '../clients/utils'

const initialState = null as null | string

const authenticationTokenUpdated = (
  state: string | null,
  action: PayloadAction<string>
): string => {
  return action.payload
}

const authenticationTokenSlice = createSlice({
  name: 'authenticationToken',
  initialState,
  reducers: {
    authenticationTokenUpdated,
  },
})

export const getAuthenticationToken = async (dispatch: AppDispatch, getState: () => RootState): Promise<string | null> {
    const state = getState()

    if (state.authenticationToken) {
      return state.authenticationToken
    }

    const token = await retrieveAuthenticationToken()
    if (token) {
      dispatch(
        authenticationTokenSlice.actions.authenticationTokenUpdated(token)
      )
    }

    return token
}

export default authenticationTokenSlice.reducer
