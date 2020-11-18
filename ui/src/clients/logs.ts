import request from './request'

export type DateTime = string

export interface Log {
  id: number
  md5hash: string
  last_seen: DateTime
  created: DateTime
  error: boolean
  silent: boolean
  message: string
  count: number
}

export async function getLogs(): Promise<Log[]> {
  return request<Log[]>('GET', 'activity-logs', {})
}

export async function getLog(id: number): Promise<Log> {
  return request<Log>('GET', `activity-logs/${id}`, {})
}
