import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RootState} from '../../store'

const Trello: FunctionComponent = () => {
  const trelloBoardUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.trello_board_url : null
  )
  const resetTrelloSettings = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.urls?.trello_reset_url : null
  )
  const resyncTrello = useSelector((state: RootState) =>
    state.status.logged_in
      ? state.status.urls?.trello_resynchronization_url
      : null
  )

  return (
    <>
      <div id="trello" className="content">
        <div className="row">
          <div className="large-12 columns">
            <p>
              Inthe.AM provides Trello integration so you can manage your tasks
              on a Trello board, too.
            </p>
          </div>
        </div>
        <div className="row">
          <div className="large-12 columns">
            {trelloBoardUrl && (
              <>
                <p>
                  Trello integration is currently turned on; you can access your
                  Trello board by clicking the 'Trello' button at the top of
                  your screen, or by going to the following URL:
                </p>
                <ul>
                  <li>
                    <a href={trelloBoardUrl}>{trelloBoardUrl}</a>.
                  </li>
                </ul>
              </>
            )}
            {!trelloBoardUrl && (
              <p>
                Once Trello integration is turned on, Inthe.AM will
                automatically create a new Trello board on your account. All of
                your pending tasks will be displayed on the board in various
                columns, and any changes you make on Inthe.AM, using any
                Taskwarrior clients synchronizing with Inthe.AM, or directly on
                your Trello board will automatically be synchronized.
              </p>
            )}
            <p>Protips:</p>
            <ul>
              <li>
                Trello labels are mapped to slugified tag names on tasks. That
                is to say that if you have a label in Trello named "My Project",
                it will appear on relevant tasks as a tag named "my-project" and
                vice-versa.
              </li>
              <li>
                You can change the list a task is displayed on by changing the
                value of the field{' '}
                <span className="code">intheamtrellolistname</span>.
              </li>
              <li>
                You can change the description of a task by changing he value of
                the field <span className="code">intheamtrellodescription</span>
                .
              </li>
            </ul>
            <p>Please:</p>
            <ul>
              <li>
                Do not delete your "To Do" list! Inthe.AM will add tasks to that
                list when you create them!
              </li>
              <li>
                Do not change the values of the following fields -- they may
                cause Inthe.AM to have difficulty synchronizing with your Trello
                account:
                <ul>
                  <li>
                    <span className="code">intheamtrelloid</span>
                  </li>
                  <li>
                    <span className="code">intheamtrelloboardid</span>
                  </li>
                  <li>
                    <span className="code">intheamtrellourl</span>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
        <div className="row">
          <div className="large-12 columns">
            {trelloBoardUrl && resetTrelloSettings && resyncTrello && (
              <>
                <a href={resetTrelloSettings} className="button radius alert">
                  Reset Trello settings
                </a>
                <a href={resyncTrello} className="button radius">
                  Force Resynchronization
                </a>
              </>
            )}
            {!trelloBoardUrl && (
              <>
                <a
                  className="button radius"
                  href="{{applicationController.urls.trello_authorization_url }}?api_key={{ applicationController.user.api_key }}"
                >
                  Click here to get started
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default Trello
