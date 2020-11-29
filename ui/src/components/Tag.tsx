import React, {FunctionComponent} from 'react'
import Icon from './Icon'

export interface Props {
  name: string
}

const Tag: FunctionComponent<Props> = ({name}) => {
  return (
    <>
      <span className="labeled-tag">
        <span className="labeled-tag-label">{name}</span>
        <Icon name="price-tag" />
      </span>
    </>
  )
}

export default Tag
