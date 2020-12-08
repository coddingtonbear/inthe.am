import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Route} from 'react-router'
import {Redirect, RouteProps} from 'react-router'
import {useToasts} from 'react-toast-notifications'
import {push} from 'connected-react-router'

import {RootState, useAppDispatch} from '../store'
import AuthenticatedFrame from './AuthenticatedFrame'
import {isOfficialServer} from '../utils/official'

const AuthenticatedRoute: FunctionComponent<RouteProps> = ({
  component,
  ...props
}) => {
  const status = useSelector((state: RootState) => state.status)
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  const ReactComponent = component as FunctionComponent

  React.useEffect(() => {
    if (status.logged_in) {
      if (!status.privacy_policy_up_to_date) {
        dispatch(push('/privacy-policy'))
        addToast('You must accept our privacy policy to continue', {
          appearance: 'warning',
        })
        return
      }
      if (!status.tos_up_to_date) {
        dispatch(push('/terms-of-service'))
        addToast('You must accept our terms of service to continue', {
          appearance: 'warning',
        })
        return
      }
    }
  }, [
    status.logged_in,
    status.logged_in && status.privacy_policy_up_to_date,
    status.logged_in && status.tos_up_to_date,
  ])

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
