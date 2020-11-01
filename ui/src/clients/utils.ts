import * as Cookie from 'es-cookie'
import axios from 'axios'

const API_BASE = '/api/v2/'

export interface AuthenticationTokenResponse {
  token: string | null
}

export async function retrieveAuthenticationToken(): Promise<string | null> {
  const response = await axios.get<AuthenticationTokenResponse>('/api/token/', {
    responseType: 'json',
  })

  return response.data.token
}

export function getCSRFToken(): string | undefined {
  return Cookie.get('csrftoken')
}

export function getApiUrl(route: string): string {
  return API_BASE + route + '/'
}
