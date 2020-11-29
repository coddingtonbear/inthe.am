import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Link} from 'react-router-dom'
import {RouteProps} from 'react-router'

import {TopBar, TopBarRight, TopBarLeft} from 'react-foundation'

import {editTaskModalActions} from '../reducers'
import {RootState, useAppDispatch} from '../store'
import {useUrls} from '../reducers/status'
import {Stream} from '../contexts/stream'
import LabeledIcon from './LabeledIcon'
import Icon from './Icon'
import {refreshTasks} from '../thunks/tasks'

interface Props extends RouteProps {
  component: FunctionComponent
}

const AuthenticatedFrame: FunctionComponent<Props> = ({
  component,
  ...props
}) => {
  const dispatch = useAppDispatch()
  const status = useSelector((state: RootState) => state.status)
  const trelloBoardUrl = useSelector((state: RootState) =>
    status.logged_in ? status.trello_board_url : null
  )
  const apiKey = useSelector((state: RootState) =>
    status.logged_in ? status.api_key : null
  )
  const streamState = React.useContext(Stream)
  const urls = useUrls()

  function onShowHelp() {}

  function onCreateTask() {
    dispatch(editTaskModalActions.selectTaskForEdit({}))
  }

  function onRefresh() {
    dispatch(refreshTasks())
  }

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
              <Link to={'/task-list'}>
                <LabeledIcon icon="results" label="Tasks" />
              </Link>
            </li>
            {trelloBoardUrl && (
              <li className="mobile-only" data-intro="alt+k">
                <a title="Trello" href={trelloBoardUrl}>
                  <LabeledIcon icon="checkbox" label="Trello" />
                </a>
              </li>
            )}

            <li className="desktop-only" data-intro="alt+t">
              <Link to={'/tasks'}>
                <LabeledIcon icon="results" label="Tasks" />
              </Link>
            </li>
            <li className="desktop-only" data-intro="alt+k">
              {trelloBoardUrl && (
                <a title="Trello" href={trelloBoardUrl}>
                  <LabeledIcon icon="checkbox" label="Trello" />
                </a>
              )}
              {!trelloBoardUrl && urls && (
                <a
                  title="Trello"
                  href={`${urls.trello_authorization_url}?api_key=${apiKey}`}
                >
                  <LabeledIcon icon="checkbox" label="Trello" />
                </a>
              )}
            </li>
            <li data-intro="alt+n">
              <a onClick={onCreateTask}>
                <LabeledIcon icon="pencil" label="New" />
              </a>
            </li>

            {streamState.stream && (
              <li id="refresh-link" data-intro="alt+r">
                <a
                  title="Connected; tasks will update automatically"
                  className="connected"
                >
                  <Icon name="refresh" />
                </a>
              </li>
            )}
            {!streamState.stream && (
              <li id="refresh-link" data-intro="alt+r">
                <a
                  onClick={onRefresh}
                  className="disconnected"
                  title="Not connected; click to refresh"
                >
                  <Icon name="refresh" />
                </a>
              </li>
            )}
          </ul>
        </TopBarLeft>
        <TopBarRight>
          <ul className="dropdown menu">
            <li className="desktop-only">
              <a title="Help" onClick={onShowHelp}>
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
                <LabeledIcon icon="list" label="Log" />
              </Link>
            </li>
            <li data-intro="alt+/">
              <Link to={'/configure'}>
                <LabeledIcon icon="widget" label="Configuration" />
              </Link>
            </li>
            {urls && (
              <li data-intro="alt+x">
                <a href={urls.logout}>
                  <LabeledIcon icon="eject" label="Log Out" />
                </a>
              </li>
            )}
          </ul>
        </TopBarRight>
      </TopBar>
      <ReactComponent {...props} />
    </>
  )
}

export default AuthenticatedFrame
