import {Task} from '../clients/tasks'

export const taskIsEditable = (task: Task): boolean => {
  return ['pending', 'waiting'].includes(task.status)
}

export const getBlockedTasks = (tasks: Task[], task: Task): Task[] => {
  return tasks.filter(
    (otherTask) =>
      taskIsEditable(otherTask) &&
      task.blocks &&
      task.blocks.includes(otherTask.uuid)
  )
}

export const getBlockingTasks = (tasks: Task[], task: Task): Task[] => {
  const blockingTasks: Task[] = []

  for (const otherTask of tasks) {
    if (
      otherTask.blocks &&
      otherTask.blocks.includes(task.uuid) &&
      taskIsEditable(otherTask)
    ) {
      blockingTasks.push(otherTask)
    }
  }

  return blockingTasks
}

export const taskIsBlocking = (tasks: Task[], task: Task): boolean => {
  return getBlockedTasks(tasks, task).length > 0
}

export const taskIsBlocked = (tasks: Task[], task: Task): boolean => {
  return getBlockingTasks(tasks, task).length > 0
}
