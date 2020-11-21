import React, {ChangeEvent, FormEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Button, Callout, Colors} from 'react-foundation'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'

interface TaskEmailLinkProps {
  suffix?: string
}

const TaskEmailLink: FunctionComponent<TaskEmailLinkProps> = ({
  suffix = '',
}) => {
  const status = useSelector((state: RootState) => state.status)

  if (status.logged_in !== true) {
    return <></>
  }

  const [username, domain] = status.task_creation_email_address.split('@')

  const fullEmail = username + suffix + '@' + domain

  return <a href={'mailto:' + fullEmail}>{fullEmail}</a>
}

const Email: FunctionComponent = () => {
  const status = useSelector((state: RootState) => state.status)
  const [whitelist, setWhitelist] = React.useState<string>(
    status.logged_in ? status.email_whitelist : ''
  )
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  if (status.logged_in !== true) {
    return <></>
  }

  function onChangeWhitelist(evt: ChangeEvent<HTMLTextAreaElement>) {
    setWhitelist(evt.target.value)
  }

  function onSaveWhitelist() {
    if (!status.urls?.email_integration) {
      throw Error('No passlist URL found')
    }

    const data = new FormData()
    data.set('email_whitelist', whitelist)

    request('POST', status.urls.email_integration, {
      data: data,
      lookupApiUrl: false,
    }).then(() => {
      addToast('E-mail passlist updated', {appearance: 'success'})
      dispatch(refreshStatus())
    })
  }

  return (
    <>
      <div className="row">
        <div className="large-12 columns">
          <h3>E-mail-to-Task</h3>
          <p>Inthe.AM can receive and add items to your task list via email.</p>
          {!status.email_whitelist && (
            <Callout color={Colors.WARNING}>
              For your security, the ability to receive tasks via email requires
              that you enter email addresses into the passlist below to prevent
              others from being able to add tasks to your task list.
            </Callout>
          )}
          {status.email_whitelist && (
            <>
              <table className="pure-table pure-table-horizontal">
                <tbody>
                  <tr>
                    <th>Your Inthe.AM email address</th>
                    <td>
                      <TaskEmailLink />
                    </td>
                  </tr>
                </tbody>
              </table>
              <p>
                Simply send an email to {status.task_creation_email_address}
                with either an empty subject or the word <strong>New</strong>,
                and a body containing the text you would use on the command-line
                to create a task.
              </p>
              <p>For example:</p>
              <blockquote>
                From: {status.email}
                <br />
                To: {status.task_creation_email_address}
                <br />
                Subject: New
                <br />
                <br />
                Find local source for flux capacitor parts. project:time_machine
                priority:h +delorean
              </blockquote>
              <h4>Advanced Use</h4>
              <p>
                Although setting task attributes in the body of the email itself
                will work just fine, you can also specify task attributes or
                tags by adding suffixes to the email address itself.
              </p>
              <p>
                For example, to automatically add the tag "alpha" to an incoming
                task, you can send an email to <TaskEmailLink suffix="+alpha" />{' '}
                or to set the project to "time_machine" you could send an email
                to <TaskEmailLink suffix="__project=time_machine" />
              </p>
              <p>
                Tags and task attributes can be assigned simultaneously for any
                task attribute including any UDAs you might have specified, and
                you may specify any number of them simultaneously (for example,
                this one sets priority, project and adds two tags:{' '}
                <TaskEmailLink suffix="+one__project=time_machine__priority=H+two" />
                ) just be sure to follow the following format:
              </p>
              <table>
                <tbody>
                  <tr>
                    <th>Tags</th>
                    <td>
                      <code>+&lt;TAG&gt;</code>
                    </td>
                  </tr>
                  <tr>
                    <th>Attributes</th>
                    <td>
                      <code>__&lt;ATTRIBUTE&gt;=&lt;VALUE&gt;</code>
                      (Note: the &lt;ATTRIBUTE&gt; is prefixed with{' '}
                      <strong>two</strong> underscores.)
                    </td>
                  </tr>
                </tbody>
              </table>
            </>
          )}
        </div>
        <div className="large-12 columns">
          <label>Email Address Passlist</label>
          <textarea
            onChange={onChangeWhitelist}
            placeholder="me@somesite.com"
            value={whitelist}
          />
          <Callout color={Colors.PRIMARY}>
            Only email messages received from addresses matching one of the
            above passlisted email addresses will be accepted. Please enter only
            one email address per line. You may use '*' and '?' for more
            sophisticated email matching.
          </Callout>
          <Button onClick={onSaveWhitelist}>Save Passlist</Button>
        </div>
      </div>
    </>
  )
}

export default Email
