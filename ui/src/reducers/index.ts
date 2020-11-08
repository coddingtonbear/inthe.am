import {createBrowserHistory} from 'history'
import {combineReducers} from 'redux'
import {connectRouter} from 'connected-react-router'

import status from './status'
import tasks from './tasks'
import annotationModal from './annotationModal'
import editTaskModal from './editTaskModal'

const createRootReducer = (history: ReturnType<typeof createBrowserHistory>) =>
  combineReducers({
    router: connectRouter(history),
    status: status.reducer,
    tasks: tasks.reducer,
    annotationModal: annotationModal.reducer,
    editTaskModal: editTaskModal.reducer,
  })

export default createRootReducer
export const {actions: taskActions} = tasks
export const {actions: annotationModalActions} = annotationModal
export const {actions: statusActions} = status
export const {actions: editTaskModalActions} = editTaskModal
