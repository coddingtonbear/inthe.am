import React, {FunctionComponent} from 'react'

import {Callout, Colors} from 'react-foundation'

const Zapier: FunctionComponent = () => {
  return (
    <>
      <div id="zapier-integration" className="content">
        <div className="row">
          <div className="large-12 columns">
            <h3>Zapier Integration</h3>
            <p>
              Using Zapier, you can integrate your Taskwarrior task list with
              other services by either creating new tasks in your task list when
              something happens in another service, or doing something in
              another service when a task is created or changed on your task
              list.
            </p>
            <table className="pure-table pure-table-horizontal">
              <tbody>
                <tr>
                  <th>Beta Access URL:</th>
                  <td>
                    <a href="https://zapier.com/platform/public-invite/208/fb980a74a7d3efada0fa7ba221190817/">
                      https://zapier.com/platform/public-invite/208/fb980a74a7d3efada0fa7ba221190817/
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
            <Callout color={Colors.PRIMARY}>
              <strong>This is a BETA feature</strong>; don't expect everything
              to work perfectly! If you have any questions or run into any
              trouble, though, please join Inthe.AM's{' '}
              <a href="https://gitter.im/coddingtonbear/inthe.am">
                gitter channel
              </a>
              .
            </Callout>
          </div>
        </div>
      </div>
    </>
  )
}

export default Zapier
