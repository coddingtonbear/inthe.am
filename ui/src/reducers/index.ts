import {createBrowserHistory} from 'history'
import {combineReducers} from 'redux'
import {connectRouter} from 'connected-react-router'

import status from './status'
import authenticationToken from './authenticationToken'
import tasks from './tasks'

const createRootReducer = (history: ReturnType<typeof createBrowserHistory>) =>
  combineReducers({
    router: connectRouter(history),
    status,
    authenticationToken,
    tasks,
  })
export default createRootReducer
