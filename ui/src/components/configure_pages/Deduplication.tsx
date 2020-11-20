import React, {FormEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Button, Switch} from 'react-foundation'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'

const Deduplication: FunctionComponent = () => {
  const stateIsEnabled = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.auto_deduplicate : false
  )
  const deduplicationUrl = useSelector(
    (state: RootState) => state.status.urls?.deduplicate_tasks
  )
  const deduplicationConfigUrl = useSelector(
    (state: RootState) => state.status.urls?.deduplication_config
  )
  const [enabled, setEnabled] = React.useState<boolean>(stateIsEnabled)
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  function deduplicateNow() {
    if (!deduplicationUrl) {
      throw Error('No deduplication URL found')
    }

    request('POST', deduplicationUrl, {
      data: '',
      lookupApiUrl: false,
    }).then(() => {
      addToast('Task deduplication started', {appearance: 'success'})
      dispatch(refreshStatus())
    })
  }

  function onChange(evt: FormEvent) {
    const newValue = !enabled
    setEnabled(newValue)

    if (!deduplicationConfigUrl) {
      throw Error('No deduplication URL found')
    }

    const formData = new FormData()
    formData.set('enabled', newValue ? '1' : '0')

    request('POST', deduplicationConfigUrl, {
      data: formData,
      lookupApiUrl: false,
    }).then(() => {
      const message = newValue
        ? 'Automatic deduplication enabled'
        : 'Automatic deduplication disabled'

      addToast(message, {appearance: 'success'})
      dispatch(refreshStatus())
    })
  }

  return (
    <>
      <div id="deduplicate" className="content">
        <div className="row">
          <div className="large-12 columns">
            <h3>Task Deduplication</h3>
            <p>
              <strong>BETA:</strong> Inthe.AM provides basic task de-duplication
              for recurring events that may have been created by multiple
              devices.
            </p>
          </div>
        </div>
        <div className="row">
          <div className="large-12 columns">
            <p>Automatically de-duplicate tasks?</p>
            <Switch
              input={{
                type: 'checkbox',
                checked: enabled,
                onChange: onChange,
              }}
              active={{text: 'On'}}
              inactive={{text: 'Off'}}
            />
          </div>
        </div>
        <div className="row">
          <div className="large-12 columns">
            If you have tasks that are currently in need of deduplication, you
            can deduplicate your tasks by clicking the below button.
          </div>
          <Button onClick={deduplicateNow}>Deduplicate tasks now</Button>
        </div>
      </div>
    </>
  )
}

export default Deduplication
