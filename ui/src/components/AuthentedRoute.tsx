import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Redirect, RouteProps} from 'react-router'

import {RootState} from '../store'

const AuthenticatedRoute: FunctionComponent<RouteProps> = ({
  component,
  ...props
}) => {
  const isLoggedIn = useSelector((state: RootState) => state.status.logged_in)
  const ReactComponent = component as FunctionComponent

  if (!isLoggedIn) {
    return <Redirect to="/" />
  }

  return <ReactComponent {...props} />
}

export default AuthenticatedRoute
