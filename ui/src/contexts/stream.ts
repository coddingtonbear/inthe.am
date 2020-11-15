import React from 'react'

export interface StreamContext {
  stream?: EventSource
}

export const Stream = React.createContext<StreamContext>({})
