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

  async function runDangerZoneTask(
    url: string | undefined,
    successMessage: string
  ): Promise<void> {
    if (!url) {
      throw Error('No URL provided!')
    }

    return request('POST', url, {
      data: '',
      lookupApiUrl: false,
    }).then(() => {
      addToast(successMessage, {appearance: 'success'})
      dispatch(refreshStatus())
    }).catch((error) => {
      if (error.response) {
        addToast(
          <>
            An error occurred while handling your request!<br /><br/>
            HTTP {error.response.status}
          </>,
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
          <h3>Delete your account's task data</h3>
          <p>
            Pressing this button will delete both any task information currently
            stored in your task list on Inthe.AM, as well as clear any
            information stored in your Inthe.AM taskserver account.
          </p>
          <p>
            You might want to use this function when you would like to
            reset the task information shown on Inthe.AM and your
            Taskserver account.
          </p>
          <p>
            Although executing this operation will not require you to
            re-configure clients synchronizing with Inthe.AM's taskserver,
            you will need to at least clear any synchronizing clients'&nbsp;
            <code>backlog.data</code> for them to be able to synchronize again.
          </p>
        </div>
        <Button
          color={Colors.ALERT}
          onClick={() =>
            runDangerZoneTask(status.urls?.clear_task_data, 'Task data cleared.')
          }
        >
          Clear Task Data
        </Button>
      </div>
    </>
  )
}

export default DangerZone
