import request from './request'

type UUID = string
type DateTime = string

export interface Task {
  id: UUID
  uuid: UUID // Same as 'id'
  short_id: number
  // status: for options see https://github.com/GothenburgBitFactory/taskwarrior/blob/6727d08da05b1090e0eda2270bc35d09a4528e87/src/Task.h#L71
  status: 'pending' | 'completed' | 'deleted' | 'recurring' | 'waiting'
  urgency: number
  description: string
  priority: string // traditionally: 'H', 'M', and 'L', but configurable
  project: string
  due: DateTime
  entry: DateTime
  modified: DateTime
  start: DateTime
  wait: DateTime
  until: DateTime
  scheduled: DateTime
  depends: UUID[]
  blocks: UUID[]
  annotations: string[]
  tags: string[]
  imask: string
  udas: {
    [key: string]: any | undefined
  }
}

export async function getTasks(token: string): Promise<Task[]> {
  return request<Task[]>('GET', 'tasks', {token})
}

export async function getTask(token: string, uuid: UUID): Promise<Task> {
  return request<Task>('GET', `tasks/${uuid}`, {token})
}

export async function startTask(token: string, uuid: UUID): Promise<void> {
  return request<void>('GET', `tasks/${uuid}/start`, {token})
}

export async function stopTask(token: string, uuid: UUID): Promise<void> {
  return request<void>('GET', `tasks/${uuid}/start`, {token})
}
