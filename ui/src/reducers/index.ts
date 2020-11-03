import {createBrowserHistory} from 'history'
import {combineReducers} from 'redux'
import {connectRouter} from 'connected-react-router'

import status from './status'
import tasks from './tasks'

const createRootReducer = (history: ReturnType<typeof createBrowserHistory>) =>
  combineReducers({
    router: connectRouter(history),
    status: status.reducer,
    tasks: tasks.reducer,
  })

export default createRootReducer
export const {actions: taskActions} = tasks
