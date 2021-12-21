import request from './request'

export type UUID = string
export type DateTime = string
export type JSONString = string

export interface Change {
  id: UUID
  source: {
    id: UUID
    commit_hash: string
    sourcetype: number
    sourcetype_name: string
    created: DateTime
    finished: DateTime
    foreign_id: string
  }
  task_id: UUID
  field: UUID
  data_from: JSONString
  data_to: JSONString
  changed: DateTime
}

export async function getTaskChanges(task_id: UUID): Promise<Change[]> {
  return request<Change[]>('GET', `tasks/${task_id}/changes`, {})
}
