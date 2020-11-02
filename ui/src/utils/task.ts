import {Task} from '../clients/tasks'

export const taskIsRelevant = (task: Task): boolean => {
  return !['completed', 'deleted'].includes(task.status)
}

export const taskIsBlocking = (tasks: Task[], task: Task): boolean => {
  const blockedTasks = tasks.filter(
    (otherTask) => task.blocks && task.blocks.includes(otherTask.uuid)
  )
  for (const otherTask of blockedTasks) {
    if (taskIsRelevant(otherTask)) {
      return true
    }
  }
  return false
}

export const taskIsBlocked = (tasks: Task[], task: Task): boolean => {
  for (const otherTask of tasks) {
    if (
      otherTask.blocks &&
      otherTask.blocks.includes(task.uuid) &&
      taskIsRelevant(otherTask)
    ) {
      return true
    }
  }
  return false
}
