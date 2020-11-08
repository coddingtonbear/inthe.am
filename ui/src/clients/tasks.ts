import request from './request'

export type UUID = string
export type DateTime = string

export interface Task {
  id: UUID
  uuid: UUID // Same as 'id'
  short_id: number
  // status: for options see https://github.com/GothenburgBitFactory/taskwarrior/blob/6727d08da05b1090e0eda2270bc35d09a4528e87/src/Task.h#L71
  status: 'pending' | 'completed' | 'deleted' | 'recurring' | 'waiting'
  urgency: number
  description: string
  priority?: string // traditionally: 'H', 'M', and 'L', but configurable
  project?: string
  due?: DateTime
  entry: DateTime
  modified: DateTime
  start?: DateTime
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

export interface TaskUpdate extends Partial<Task> {}

export async function getTasks(): Promise<Task[]> {
  return request<Task[]>('GET', 'tasks', {})
}

export async function getTask(uuid: UUID): Promise<Task> {
  return request<Task>('GET', `tasks/${uuid}`, {})
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
