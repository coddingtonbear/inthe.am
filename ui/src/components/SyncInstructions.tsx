import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {RootState} from '../store'

import {Callout, Colors} from 'react-foundation'

const SyncInstructions: FunctionComponent = () => {
  const myCertificate = useSelector(
    (state: RootState) => state.status.urls?.my_certificate
  )
  const myKey = useSelector((state: RootState) => state.status.urls?.my_key)
  const caCertificate = useSelector(
    (state: RootState) => state.status.urls?.ca_certificate
  )
  const taskdServer = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.taskd_server : null
  )
  const taskdCredentials = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.taskd_credentials : null
  )

  return (
    <>
      <Callout color={Colors.PRIMARY}>
        You can make the process of configuring Taskwarrior to synchronize with
        Inthe.AM a little easier by installing and using the&nbsp;
        <a href="http://github.com/coddingtonbear/taskwarrior-inthe.am">
          Taskwarrior Inthe.AM Utility's
        </a>
        &nbsp;
        <b>setup</b> command rather than following the below instructions.
      </Callout>
      <table className="pure-table pure-table-horizontal">
        <tbody>
          {myCertificate && (
            <tr>
              <th>Your Certificate</th>
              <td>
                <a href={myCertificate}>private.certificate.pem</a>
              </td>
            </tr>
          )}
          {myKey && (
            <tr>
              <th>Your Key</th>
              <td>
                <a href={myKey}>private.key.pem</a>
              </td>
            </tr>
          )}
          {caCertificate && (
            <tr>
              <th>Server Certificate</th>
              <td>
                <a href={caCertificate}>ca.cert.pem</a>
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <p>
        Add the following settings to your Taskwarrior configuration file (
        <code>~/.taskrc</code>).
      </p>

      <code className="para">
        taskd.certificate=/path/to/private.certificate.pem
        <br />
        taskd.key=/path/to/private.key.pem
        <br />
        taskd.ca=/path/to/ca.cert.pem
        <br />
        taskd.server={taskdServer}
        <br />
        taskd.credentials={taskdCredentials}
        <br />
        taskd.trust=ignore hostname
        <br />
      </code>

      <p>
        Synchronizing for the first time is as easy as running{' '}
        <code>task sync init</code>
        &mdash; running that command will instruct Taskwarrior to send all of
        its tasks to Inthe.AM. After the initial synchronization, you can
        synchronize with Inthe.AM by running <code>task sync</code>.
      </p>
    </>
  )
}

export default SyncInstructions
