import axios from 'axios'

import {getApiUrl, getCSRFToken} from './utils'
import {getAuthenticationToken} from '../reducers/authenticationToken'

export interface UdaDefinition {
  field: string
  label: string
  type: string
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
}

export interface UnauthenticatedStatus {
  logged_in: false
}

export type Status = AuthenticatedStatus | UnauthenticatedStatus

export async function getStatus(token: string): Promise<Status> {
  const response = await axios.get(getApiUrl('user/status'), {
    responseType: 'json',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      Authorization: `Token ${token}`,
    },
  })
  return response.data
}
