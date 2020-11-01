import {createBrowserHistory} from 'history'
import {configureStore} from '@reduxjs/toolkit'
import {useDispatch} from 'react-redux'
import createRootReducer from './reducers'
import {routerMiddleware} from 'connected-react-router'

export const history = createBrowserHistory()

const rootReducer = createRootReducer(history)

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(routerMiddleware(history)),
})

export type RootState = ReturnType<typeof rootReducer>
export type AppDispatch = typeof store.dispatch
export const useAppDispatch = () => useDispatch<AppDispatch>()

export default store
