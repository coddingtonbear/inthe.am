import React, {ChangeEvent, FunctionComponent} from 'react'
import {Button} from 'react-foundation'
import {useSelector} from 'react-redux'
import {Callout, Colors} from 'react-foundation'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'

const TaskRc: FunctionComponent = () => {
  const taskRcData = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.taskrc_extras : ''
  )
  const taskrcExtrasUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.urls?.taskrc_extras : null
  )
  const [taskRc, setTaskRc] = React.useState<string>(taskRcData)
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  function onChangeTaskrc(event: ChangeEvent<HTMLTextAreaElement>) {
    setTaskRc(event.target.value)
  }

  function onSaveTaskrc() {
    if (!taskrcExtrasUrl) {
      throw new Error('No taskrc extras URL found')
    }

    request('PUT', taskrcExtrasUrl, {
      data: taskRc,
      lookupApiUrl: false,
    }).then(() => {
      dispatch(refreshStatus())
      addToast('TaskRc Extras updated.', {appearance: 'success'})
    })
  }

  return (
    <div className="row">
      <div className="large-12 columns">
        <h3>TaskRc Extras</h3>
        <textarea onChange={onChangeTaskrc} value={taskRc} />
        <Callout color={Colors.PRIMARY}>
          Only configuration values relating to urgency or UDA definitions will
          have an effect, but entering your entire local{' '}
          <span className="code">.taskrc</span> is both safe and encouraged.
        </Callout>
        <Button onClick={onSaveTaskrc}>Save Taskrc</Button>
      </div>
    </div>
  )
}

export default TaskRc
