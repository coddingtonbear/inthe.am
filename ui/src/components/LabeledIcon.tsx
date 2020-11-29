import React, {FunctionComponent} from 'react'
import Icon from './Icon'

export interface Props {
  label: string
  icon: string
}

const LabeledIcon: FunctionComponent<Props> = ({label, icon}) => {
  return (
    <>
      <span className="labeled-icon-container">
        <Icon name={icon} title={label} />
        <span className="labeled-icon-label">{label}</span>
      </span>
    </>
  )
}

export default LabeledIcon
