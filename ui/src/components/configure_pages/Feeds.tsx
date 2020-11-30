import React, {ChangeEvent, FunctionComponent} from 'react'
import {Switch} from 'react-foundation'
import {useSelector} from 'react-redux'
import {Callout, Colors} from 'react-foundation'
import {useToasts} from 'react-toast-notifications'

import request from '../../clients/request'
import {RootState, useAppDispatch} from '../../store'
import {refreshStatus} from '../../thunks/status'

const Feeds: FunctionComponent = () => {
  const icalConfigUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.urls?.configure_ical : null
  )
  const icalState = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.ical_enabled : false
  )
  const icalDueUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.ical_due_url : null
  )
  const icalWaitingUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.ical_waiting_url : null
  )
  const [icalEnabled, setIcalEnabled] = React.useState<boolean>(icalState)

  const rssConfigUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.urls?.configure_feed : null
  )
  const rssState = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.feed_enabled : false
  )
  const rssUrl = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.feed_url : null
  )
  const [rssEnabled, setRssEnabled] = React.useState<boolean>(rssState)

  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  function onChangeIcal(evt: ChangeEvent<HTMLInputElement>) {
    const newValue = !icalEnabled
    setIcalEnabled(newValue)

    if (!icalConfigUrl) {
      throw Error('No ical configuration url found')
    }

    const formData = new FormData()
    formData.set('enabled', newValue ? '1' : '0')

    request('POST', icalConfigUrl, {
      data: formData,
      lookupApiUrl: false,
    }).then(() => {
      const message = newValue ? 'iCal Feed enabled' : 'iCal Feed disabled'

      addToast(message, {appearance: 'success'})
      dispatch(refreshStatus())
    })
  }

  function onChangeRss(evt: ChangeEvent<HTMLInputElement>) {
    const newValue = !rssEnabled
    setRssEnabled(newValue)

    if (!rssConfigUrl) {
      throw Error('No rss configuration url found')
    }

    const formData = new FormData()
    formData.set('enabled', newValue ? '1' : '0')

    request('POST', rssConfigUrl, {
      data: formData,
      lookupApiUrl: false,
    }).then(() => {
      const message = newValue ? 'RSS Feed enabled' : 'RSS Feed disabled'

      addToast(message, {appearance: 'success'})
      dispatch(refreshStatus())
    })
  }

  return (
    <>
      <div className="row">
        <div className="large-12 columns">
          <h3>iCal Feed</h3>
          <p>
            Turn this feature on to gain access to two different iCal feeds that
            you can add to either your Google Calendar or any other calendaring
            application that supports the iCal standard.
          </p>
          {!icalState && (
            <Callout color={Colors.WARNING}>
              For your security, your iCal feed is disabled by default. Although
              your iCal feed's URL is unique and randomly generated, no
              authentication is used to improve compatibility with iCal feed
              readers.
            </Callout>
          )}
          {icalState && (
            <table className="pure-table pure-table-horizontal">
              <tbody>
                <tr>
                  <th>Task Due Dates iCal Feed URL</th>
                  <td>https://inthe.am{icalDueUrl}</td>
                </tr>
                <tr>
                  <th>Task Waiting Dates iCal Feed URL</th>
                  <td>https://inthe.am{icalWaitingUrl}</td>
                </tr>
              </tbody>
            </table>
          )}
          <label>iCal Task Feed</label>
          <Switch
            input={{
              type: 'checkbox',
              checked: icalEnabled,
              onChange: onChangeIcal,
            }}
            active={{text: 'On'}}
            inactive={{text: 'Off'}}
          />
        </div>
      </div>
      <div className="row">
        <div className="large-12 columns">
          <h3>RSS Feed</h3>
          <p>
            Turn this feature on to gain access to an RSS feed listing your most
            urgent tasks.
          </p>
          {!rssState && (
            <Callout color={Colors.WARNING}>
              For your security, your feed is disabled by default. Although your
              feed's URL is unique and randomly generated, no authentication is
              used to improve compatibility with RSS feed readers.
            </Callout>
          )}
          {rssState && (
            <table className="pure-table pure-table-horizontal">
              <tbody>
                <tr>
                  <th>Feed URL</th>
                  <td>https://inthe.am{rssUrl}</td>
                </tr>
              </tbody>
            </table>
          )}
          <label>RSS Task Feed</label>
          <Switch
            input={{
              type: 'checkbox',
              checked: rssEnabled,
              onChange: onChangeRss,
            }}
            active={{text: 'On'}}
            inactive={{text: 'Off'}}
          />
        </div>
      </div>
    </>
  )
}

export default Feeds
