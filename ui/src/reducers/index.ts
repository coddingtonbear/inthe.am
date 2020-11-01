import {createBrowserHistory} from 'history'
import {combineReducers} from 'redux'
import {connectRouter} from 'connected-react-router'

import status from './status'
import authenticationToken from './authenticationToken'

const createRootReducer = (history: ReturnType<typeof createBrowserHistory>) =>
  combineReducers({
    router: connectRouter(history),
    status,
    authenticationToken,
  })
export default createRootReducer
