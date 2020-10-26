import {createBrowserHistory} from 'history'
import {combineReducers} from 'redux'
import {connectRouter} from 'connected-react-router'

const createRootReducer = (history: ReturnType<typeof createBrowserHistory>) =>
  combineReducers({
    router: connectRouter(history),
  })
export default createRootReducer
