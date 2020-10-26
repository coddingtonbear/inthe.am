import {createBrowserHistory} from 'history'
import {configureStore} from '@reduxjs/toolkit'
import {useDispatch} from 'react-redux'
import createRootReducer from './reducers'
import {routerMiddleware} from 'connected-react-router'

export const history = createBrowserHistory()

const store = configureStore({
  reducer: createRootReducer(history),
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(routerMiddleware(history)),
})

export type AppDispatch = typeof store.dispatch
export const useAppDispatch = () => useDispatch<AppDispatch>()

export default store
