import React, {FunctionComponent} from 'react'
import {Icon as FoundationIcon} from 'react-foundation'

export interface Props {
  name: string
  [key: string]: string
}

export const Icon: FunctionComponent<Props> = ({name, ...rest}) => {
  return <FoundationIcon prefix="fi" name={name} {...rest} />
}

export default Icon
