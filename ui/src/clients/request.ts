import axios, {AxiosRequestConfig} from 'axios'

import {getApiUrl, getCSRFToken} from './utils'

export interface RequestParams extends AxiosRequestConfig {
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
        console.error(
          "An error response was received: ",
          error.response.status,
          error.response.data,
          error.response.headers,
          error.config,
        )
      } else if (error.request) {
        console.error(
          "An error occurred while creating a request: ",
          error.request,
          error.config,
        )
      } else {
        console.error(
          "An error occurred while dispatching a request: ",
          error.request,
          error.config,
        )
      }

      throw error
    })

  return response.data
}

export default request
