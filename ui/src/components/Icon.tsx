import React, {FunctionComponent} from 'react'
import {Icon as FoundationIcon} from 'react-foundation'

export interface Props {
  name: string
}

export const Icon: FunctionComponent<Props> = ({name}) => {
  return <FoundationIcon prefix="fi" name={name} />
}

export default Icon
