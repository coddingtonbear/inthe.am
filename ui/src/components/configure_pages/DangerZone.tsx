import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Button, Colors} from 'react-foundation'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'

const DangerZone: FunctionComponent = () => {
  const status = useSelector((state: RootState) => state.status)
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  if (status.logged_in !== true) {
    return <></>
  }

  function runDangerZoneTask(
    url: string | undefined,
    successMessage: string
  ): void {
    if (!url) {
      throw Error('No URL provided!')
    }

    request('POST', url, {
      data: '',
      lookupApiUrl: false,
    }).then(() => {
      addToast(successMessage, {appearance: 'success'})
      dispatch(refreshStatus())
    }).catch((error) => {
      if (error.response) {
        addToast(
          `An error occurred while handling your request! HTTP ${error.response.status}`,
          {appearance: 'error'}
        )
      } else {
        addToast(
          "An error occurred while handling your request!",
          {appearance: 'error'}
        )
      }
    })
  }

  return (
    <>
      <div className="row">
        <div className="large-12 columns">
          <h3>Delete your account information</h3>
          <p>
            Pressing this button will delete both any task information currently
            stored in your task list on Inthe.AM, as well as clear any
            information stored in your Inthe.AM taskserver account.
          </p>
        </div>
      </div>
      <Button
        color={Colors.ALERT}
        onClick={() =>
          runDangerZoneTask(status.urls?.clear_task_data, 'Task data cleared')
        }
      >
        Clear Task Data
      </Button>
      <div className="row">
        <div className="large-12 columns">
          <h3>Revert task list to earlier version</h3>
          <p>
            In rare situations, the local task list that Inthe.AM uses for
            interacting with your tasks may become corrupted. You can use this
            button to reset your task list to the state it was in right before
            the most recent change.
          </p>
          <p>
            This operation is not dangerous to use on task lists that are
            properly synchronized, but there are slight dangers that information
            might be lost. Please use this button only if you're absolutely sure
            it's necessary.
          </p>
        </div>
      </div>
      <Button
        color={Colors.ALERT}
        onClick={() =>
          runDangerZoneTask(
            status.urls?.revert_to_last_commit,
            'Task data reverted to last commit'
          )
        }
      >
        Revert task list to earlier commit
      </Button>
      <div className="row">
        <div className="large-12 columns">
          <h3>Manually unlock task list</h3>
          <p>
            Pressing this button will unlock your task list. To prevent multiple
            actions from altering your taskwarrior task list simultaneously, a
            lock is used. Deleting this lock while an action is taking place is
            dangerous! Although locks do time out on their own, this button
            provides you an avenue for unlocking your repository manually.
          </p>
        </div>
      </div>
      <Button
        color={Colors.ALERT}
        onClick={() =>
          runDangerZoneTask(status.urls?.clear_lock, 'Task list unlocked')
        }
      >
        Manually unlock task list
      </Button>
      <div className="row">
        <div className="large-12 columns">
          <h3>Reset Taskserver Synchronization Settings</h3>
          <p>
            Strictly speaking, this isn't all that dangerous. Pressing this
            button will clear your Inthe.AM Taskserver account's information and
            reset your synchronization settings such that Inthe.AM will sync
            with the built-in Taskserver.
          </p>
          <p>
            If you are currently synchronizing your tasks with Inthe.AM from
            somewhere and receive a message "500 Client sync key not found"
            after pressing this button, you need to delete the "backlog.data"
            file from your tasks folder.
          </p>
        </div>
      </div>
      <Button
        color={Colors.ALERT}
        onClick={() =>
          runDangerZoneTask(
            status.urls?.taskd_reset,
            'Taskserver settings reset'
          )
        }
      >
        Reset taskserver settings
      </Button>
      <div className="row">
        <div className="large-12 columns">
          <h3>Regenerate Taskserver Certificates</h3>
          <p>
            This button will simply re-generate your Taskserver certificates. It
            is strongly recommended that you walk through the setup instructions
            described above in 'Synchronization Settings' after pressing this
            button.
          </p>
        </div>
      </div>
      <Button
        color={Colors.ALERT}
        onClick={() =>
          runDangerZoneTask(
            status.urls?.generate_new_certificate,
            'Re-generate taskserver certificates'
          )
        }
      >
        Reset taskserver certificates
      </Button>
    </>
  )
}

export default DangerZone
