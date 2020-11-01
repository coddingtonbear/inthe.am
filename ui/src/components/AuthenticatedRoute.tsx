import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Redirect, RouteProps} from 'react-router'
import {Link} from 'react-router-dom'
import {AuthenticatedStatus} from '../clients/status'
import {TopBar, TopBarRight, TopBarLeft, TopBarTitle} from 'react-foundation'

import {RootState} from '../store'
import {useUrls} from '../reducers/status'
import Icon from './Icon'

const userIsAuthenticated = (
  status: RootState['status']
): status is AuthenticatedStatus => {
  return status.logged_in
}

const AuthenticatedRoute: FunctionComponent<RouteProps> = ({
  component,
  ...props
}) => {
  const status = useSelector((state: RootState) => state.status)
  const trelloBoardUrl = useSelector((state: RootState) =>
    status.logged_in ? status.trello_board_url : null
  )
  const apiKey = useSelector((state: RootState) =>
    status.logged_in ? status.api_key : null
  )
  const urls = useUrls()

  if (!userIsAuthenticated(status)) {
    return <Redirect to="/" />
  }

  function showHelp() {}

  function createTask() {}

  function refresh() {}

  const ReactComponent = component as FunctionComponent
  return (
    <>
      <TopBar>
        <TopBarLeft>
          <ul className="dropdown menu">
            <li className="home">
              <a href="/">
                <img src="/assets/logo.png" />
                Inthe.AM
              </a>
            </li>
            <li className="mobile-only" data-intro="alt+t">
              <a href="/mobile-tasks/">
                <Icon name="results" />
                Tasks
              </a>
            </li>
            {trelloBoardUrl && (
              <li className="mobile-only" data-intro="alt+k">
                <a title="Trello" href={trelloBoardUrl}>
                  <Icon name="checkbox" />
                  Trello
                </a>
              </li>
            )}
            <li className="mobile-only" data-intro="alt+n">
              <Link to={'/create-task'}>
                <Icon name="pencil" />
                New
              </Link>
            </li>

            <li className="desktop-only" data-intro="alt+t">
              <Link to={'/tasks'}>
                <Icon name="results" />
                Tasks
              </Link>
            </li>
            <li className="desktop-only" data-intro="alt+k">
              {trelloBoardUrl && (
                <a title="Trello" href={trelloBoardUrl}>
                  <Icon name="checkbox" />
                  Trello
                </a>
              )}
              {!trelloBoardUrl && urls && (
                <a
                  title="Trello"
                  href={`${urls.trello_authorization_url}?api_key=${apiKey}`}
                >
                  <Icon name="checkbox" />
                  Trello
                </a>
              )}
            </li>
            <li className="desktop-only" data-intro="alt+n">
              <a onClick={createTask}>
                <Icon name="pencil" />
                New
              </a>
            </li>

            <li id="refresh-link" data-intro="alt+r">
              <a onClick={refresh}>
                <Icon name="refresh" />
              </a>
            </li>
          </ul>
        </TopBarLeft>
        <TopBarRight>
          <ul className="dropdown menu">
            <li className="desktop-only">
              <a title="Help" onClick={showHelp}>
                ?
              </a>
            </li>
            <li className="desktop-only" data-intro="alt+h">
              <a
                target="_blank"
                title="Documentation"
                href="http://intheam.readthedocs.org/en/latest/index.html"
              >
                <Icon name="book" />
              </a>
            </li>
            <li data-intro="alt+l">
              <Link to={'/activity-log'}>
                <Icon name="list" />
                Log
              </Link>
            </li>
            <li data-intro="alt+/">
              <Link to={'/configure'}>
                <Icon name="widget" />
                Configuration
              </Link>
            </li>
            <li data-intro="alt+x">
              <Link to={'/logout'}>
                <Icon name="eject" />
                Log Out
              </Link>
            </li>
          </ul>
        </TopBarRight>
      </TopBar>
      <ReactComponent {...props} />
    </>
  )
}

export default AuthenticatedRoute
