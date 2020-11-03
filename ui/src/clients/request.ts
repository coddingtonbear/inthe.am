import axios, {AxiosRequestConfig} from 'axios'

import {getApiUrl, getCSRFToken} from './utils'

export interface RequestParams extends AxiosRequestConfig {
  token?: string
  lookupApiUrl?: boolean
}

export async function request<T>(
  method: AxiosRequestConfig['method'],
  url: string,
  {lookupApiUrl = true, headers = {}, ...requestParams}: RequestParams
): Promise<T> {
  const requestHeaders: {[key: string]: string | undefined} = {
    'X-CSRFToken': getCSRFToken(),
  }
  Object.assign(requestHeaders, headers)

  const response = await axios
    .request({
      url: lookupApiUrl ? getApiUrl(url) : url,
      method: method,
      headers: requestHeaders,
      ...requestParams,
    })
    .catch((error) => {
      if (error.response) {
        console.log(error.response.data)
        console.log(error.response.status)
        console.log(error.response.headers)
      } else if (error.request) {
        console.log(error.request)
      } else {
        console.log(error.message)
      }
      console.log(error.config)

      throw error
    })

  return response.data
}

export default request
