import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Route} from 'react-router'
import {Redirect, RouteProps} from 'react-router'

import {RootState} from '../store'
import AuthenticatedFrame from './AuthenticatedFrame'

const AuthenticatedRoute: FunctionComponent<RouteProps> = ({
  component,
  ...props
}) => {
  const status = useSelector((state: RootState) => state.status)

  const ReactComponent = component as FunctionComponent

  return (
    <Route
      {...props}
      render={(componentProps) => {
        return (
          <>
            {status.logged_in && (
              <AuthenticatedFrame
                component={ReactComponent}
                {...componentProps}
              />
            )}
            {!status.logged_in && <Redirect to="/" />}
          </>
        )
      }}
    />
  )
}

export default AuthenticatedRoute
