import request from './request'

export type UUID = string
export type DateTime = string

// for options see class names here: https://github.com/GothenburgBitFactory/taskwarrior/blob/01696a307b6785be973e3e6428e6ade2a3872c1e/src/columns/ColUDA.h#L36
export type TaskwarriorDataType = 'string' | 'numeric' | 'date' | 'duration'

export interface Task {
  id: UUID
  uuid: UUID // Same as 'id'
  short_id: number
  // status: for options see https://github.com/GothenburgBitFactory/taskwarrior/blob/6727d08da05b1090e0eda2270bc35d09a4528e87/src/Task.h#L71
  status: 'pending' | 'completed' | 'deleted' | 'recurring' | 'waiting'
  urgency: number
  description: string
  project?: string
  due?: DateTime
  entry: DateTime
  modified: DateTime
  start?: DateTime
  end?: DateTime
  wait?: DateTime
  until?: DateTime
  scheduled?: DateTime
  depends?: UUID[]
  blocks?: UUID[]
  annotations?: string[]
  tags?: string[]
  imask?: string
  udas: {
    [key: string]: any | undefined
  }
}

export const TaskFieldTypes: {[key: string]: TaskwarriorDataType} = {
  id: 'string',
  uuid: 'string',
  short_id: 'string',
  status: 'string',
  urgency: 'numeric',
  description: 'string',
  project: 'string',
  due: 'date',
  entry: 'date',
  modified: 'date',
  start: 'date',
  end: 'date',
  wait: 'date',
  until: 'date',
  scheduled: 'date',
}

export const TaskArrayFieldTypes: {[key: string]: TaskwarriorDataType} = {
  depends: 'string',
  blocks: 'string',
  annotations: 'string',
  tags: 'string',
  imask: 'string',
}

export interface TaskUpdate extends Partial<Task> {}

export async function getTasks(): Promise<Task[]> {
  return request<Task[]>('GET', 'tasks', {})
}

export async function getTask(uuid: UUID): Promise<Task> {
  return request<Task>('GET', `tasks/${uuid}`, {})
}

export async function createTask(task: TaskUpdate): Promise<Task> {
  return request<Task>('POST', `tasks`, {
    data: task,
  })
}

export async function updateTask(task: Task): Promise<void> {
  return request<void>('PUT', `tasks/${task.uuid}`, {
    data: task,
  })
}

export async function completeTask(uuid: UUID): Promise<void> {
  return request<void>('DELETE', `tasks/${uuid}`, {})
}

export async function deleteTask(uuid: UUID): Promise<void> {
  return request<void>('POST', `tasks/${uuid}/delete`, {})
}

export async function startTask(uuid: UUID): Promise<void> {
  return request<void>('POST', `tasks/${uuid}/start`, {})
}

export async function stopTask(uuid: UUID): Promise<void> {
  return request<void>('POST', `tasks/${uuid}/stop`, {})
}
