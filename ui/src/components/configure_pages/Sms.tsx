import React, {ChangeEvent, FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Button} from 'react-foundation'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'
import {SmsReply} from '../../clients/status'

const ReplyReadableNames = [
  {
    value: SmsReply.NEVER,
    text: 'Never reply',
  },
  {
    value: SmsReply.ERROR,
    text: 'Send a reply if there was an error',
  },
  {
    value: SmsReply.ALWAYS,
    text: 'Always reply',
  },
]

const Sms: FunctionComponent = () => {
  const status = useSelector((state: RootState) => state.status)
  const [whitelist, setWhitelist] = React.useState<string>(
    status.logged_in ? status.sms_whitelist : ''
  )
  const [smsArguments, setSmsArguments] = React.useState<string>(
    status.logged_in ? status.sms_arguments : ''
  )
  const [smsReplies, setSmsReplies] = React.useState<SmsReply>(
    status.logged_in ? status.sms_replies : SmsReply.ALWAYS
  )
  const [authToken, setAuthToken] = React.useState<string>(
    status.logged_in ? status.twilio_auth_token : ''
  )
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  if (status.logged_in !== true) {
    return <></>
  }

  function onChangeWhitelist(evt: ChangeEvent<HTMLTextAreaElement>) {
    setWhitelist(evt.target.value)
  }

  function onChangeSmsArguments(evt: ChangeEvent<HTMLInputElement>) {
    setSmsArguments(evt.target.value)
  }

  function onChangeAuthToken(evt: ChangeEvent<HTMLInputElement>) {
    setAuthToken(evt.target.value)
  }

  function onChangeSmsReplies(evt: ChangeEvent<HTMLSelectElement>) {
    setSmsReplies(parseInt(evt.target.value, 10) as SmsReply)
  }

  function onSaveSms() {
    if (!status.urls?.twilio_integration) {
      throw Error('No twilio config URL found')
    }

    const data = new FormData()
    data.set('twilio_auth_token', authToken)
    data.set('sms_whitelist', whitelist)
    data.set('sms_arguments', smsArguments)
    data.set('sms_replies', smsReplies.toString())

    request('POST', status.urls.twilio_integration, {
      data: data,
      lookupApiUrl: false,
    }).then(() => {
      addToast('SMS-to-Task configuration updated', {appearance: 'success'})
      dispatch(refreshStatus())
    })
  }

  return (
    <>
      <div className="row">
        <div className="large-12 columns">
          <h3>SMS-to-Task</h3>
          <p>
            Inthe.AM can receive and add items to your task list via SMS, but it
            requires a little bit of configuration on your part.
          </p>
          <ol>
            <li>
              Sign up for a{' '}
              <a href="https://www.twilio.com/try-twilio">Twilio account</a>.
            </li>
            <li>
              Add funds to your Twilio account. Consult{' '}
              <a href="https://www.twilio.com/sms/pricing">
                Twilio's pricing structure for your country
              </a>
              ; you will need to have enough funds in your account to pay for
              your phone number (usually about 1 USD/month), and to send and
              receive text messages &mdash; generally between 0.0075 USD and
              0.10 USD/message depending upon the country of both your phone's
              phone number and the Twilio phone number you've purchased.
            </li>
            <li>
              <a href="https://www.twilio.com/user/account/phone-numbers/available/local">
                Buy a phone number
              </a>
              .
            </li>
            <li>
              From your phone number's configuration screen, set the field
              "Messaging Request URL" to your personal incoming SMS URL:{' '}
              <code>https://inthe.am{status.sms_url}</code>.
            </li>
            <li>Press save.</li>
          </ol>
          <p>
            After you have configured the above, you can send SMS messages to
            your Twilio phone number. Currently, the only command implemented is
            'add', but in the future additional commands may be added.
          </p>
          <p>
            As an example, you could add a task to the project "birthday" with a
            due date of tomorrow and high priority by sending an SMS message
            with the following contents:
          </p>
          <pre>
            add project:birthday due:tomorrow priority:h It's my birthday
          </pre>
          {!authToken && (
            <div className="block warning">
              <p>
                For your security, the ability to send task messages via SMS is
                currently disabled for your account since you have not yet
                entered your Twilio auth token.
              </p>
              <p>
                This token is necessary for verifying that incoming messages
                were sent to Inthe.AM by Twilio from your account.
              </p>
              <p>Enable SMS access by filling in the below information.</p>
            </div>
          )}
          {authToken && (
            <table className="pure-table pure-table-horizontal">
              <tbody>
                <tr>
                  <th>
                    Twilio Messaging Request URL <strong>(POST)</strong>
                  </th>
                  <td>https://inthe.am{status.sms_url}</td>
                </tr>
              </tbody>
            </table>
          )}
        </div>
        <div className="large-12 columns">
          <label>Twilio Auth Token</label>
          <input onChange={onChangeAuthToken} value={authToken} />
        </div>
        <div className="large-12 columns">
          <label>Automatic Arguments</label>
          <input onChange={onChangeSmsArguments} value={smsArguments} />
          <p className="input-note">
            Arguments to add to the 'add' command. For example, you could use
            "+sms" to add the tag "sms" to all incoming tasks.
          </p>
        </div>
        <div className="large-12 columns">
          <label>Replies</label>
          <select onChange={onChangeSmsReplies} value={smsReplies}>
            {ReplyReadableNames.map((entry) => (
              <option key={entry.value} value={entry.value}>
                {entry.text}
              </option>
            ))}
          </select>
        </div>
        <div className="large-12 columns">
          <label>Phone Number Passlist</label>
          <textarea onChange={onChangeWhitelist} value={whitelist} />
          <p className="input-note">
            One phone number per line. Leave empty to allow messages from any
            phone number.
          </p>
        </div>
      </div>
      <Button onClick={onSaveSms}>Save Settings</Button>
    </>
  )
}

export default Sms
