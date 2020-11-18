import React, {FunctionComponent} from 'react'

import {getLogs, Log} from '../clients/logs'

const ActivityLog: FunctionComponent = () => {
  const [logs, setLogs] = React.useState<Log[]>([])

  function updateLogs() {
    getLogs().then((value) => setLogs(value))
  }

  React.useEffect(updateLogs, [])

  return (
    <>
      <div className="row standalone">
        <div className="standalone">
          <div className="standalone-content">
            <h2>Activity Log</h2>
            <p>
              Here you can see any recent log messages that were generated for
              your account.
            </p>
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={2}>No log messages found</td>
                  </tr>
                )}
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td>{log.last_seen}</td>
                    <td>{log.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}

export default ActivityLog
