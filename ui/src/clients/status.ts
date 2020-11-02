import request from './request'

export interface URLList {
  login: string
  logout: string
  about: string
  generate_new_certificate: string
  ca_certificate: string
  my_certificate: string
  my_key: string
  taskrc_extras: string
  taskd_settings: string
  taskd_reset: string
  email_integration: string
  twilio_integration: string
  tos_accept: string
  privacy_policy_accept: string
  clear_task_data: string
  set_colorscheme: string
  enable_sync: string
  mirakel_configuration: string
  configure_pebble_cards: string
  configure_feed: string
  configure_ical: string
  user_status: string
  announcements: string
  refresh: string
  clear_lock: string
  sync_init: string
  revert_to_last_commit: string
  sync: string
  trello_authorization_url: string
  trello_resynchronization_url: string
  trello_reset_url: string
  deduplicate_tasks: string
  deduplication_config: string
}

export interface UdaDefinition {
  field: string
  label: string
  // type: for options see class names here: https://github.com/GothenburgBitFactory/taskwarrior/blob/01696a307b6785be973e3e6428e6ade2a3872c1e/src/columns/ColUDA.h#L36
  type: 'string' | 'numeric' | 'date' | 'duration'
}

export interface AuthenticatedStatus {
  logged_in: true
  uid: number
  username: string
  name: string
  email: string
  configured: boolean
  taskd_credentials: string
  taskd_server: string
  taskd_server_is_default: boolean
  streaming_enabled: boolean
  streaming_key: string
  taskd_files: boolean
  twilio_auth_token: string
  sms_whitelist: string
  sms_arguments: string
  sms_replies: number
  email_whitelist: string
  task_creation_email_address: string
  taskrc_extras: string
  api_key: string
  tos_up_to_date: boolean
  privacy_policy_up_to_date: boolean
  feed_url: string
  ical_waiting_url: string
  ical_due_url: string
  sms_url: string
  colorscheme: string
  repository_head: string
  sync_enabled: boolean
  pebble_cards_enabled: boolean
  feed_enabled: boolean
  ical_enabled: boolean
  auto_deduplicate: boolean
  trello_board_url: string | null
  system_udas: string
  udas: UdaDefinition[]
  urls: URLList
}

export interface UnauthenticatedStatus {
  logged_in: false
  urls?: URLList
}

export interface UndeterminedStatus {
  logged_in: null
  urls?: URLList
}

export type Status =
  | AuthenticatedStatus
  | UnauthenticatedStatus
  | UndeterminedStatus

export async function getStatus(token: string): Promise<Status> {
  return request<Status>('GET', 'user/status', {token})
}
