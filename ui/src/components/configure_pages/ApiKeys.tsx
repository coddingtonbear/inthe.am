import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'

import {RootState} from '../../store'

const ApiKeys: FunctionComponent = () => {
  const apiKey = useSelector((state: RootState) =>
    state.status.logged_in ? state.status.api_key : ''
  )

  return (
    <div className="row">
      <div className="large-12 columns">
        <h3>API Keys</h3>
        <p>
          Your Taskwarrior tasks are accessible via a RESTful API; you can use
          this to query, create, complete, or change tasks in your task list.
        </p>
        <table className="pure-table pure-table-horizontal">
          <tbody>
            <tr>
              <th>API Key</th>
              <td>
                <span id="rest_api_key">{apiKey}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p>
          For details regarding how to access and use this API, please consult
          the{' '}
          <a href="http://intheam.readthedocs.org/en/latest/api/index.html">
            API Documentation
          </a>
          .
        </p>
      </div>
    </div>
  )
}

export default ApiKeys
