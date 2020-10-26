import React, {FunctionComponent} from 'react'
import {Link} from 'react-router-dom'

import Footer from './Footer'
import SyncInstructions from './SyncInstructions'

const GettingStarted: FunctionComponent = () => {
  return (
    <div className="row standalone">
      <div className="standalone-content">
        <div className="row">
          <div className="large-12 columns">
            <h2>Let's get started</h2>
            <p>
              <strong>
                Inthe.AM is designed to augment Taskwarrior, not to replace it
              </strong>
              , so we recommend that you set up Taskwarrior to synchronize with
              Inthe.AM by following the instructions below.
            </p>
            <p>
              If you'd like to instead get started right away, you can create a
              new task by clicking the
              <i className="fa fa-pencil-square-o">New</i> icon above; you'll be
              able to find instructions for synchronizing with Inthe.AM later in
              your <Link to="/getting-started">configuration</Link>.
            </p>
          </div>
          <div className="large-12 columns">
            <div className="info-box">
              <SyncInstructions />
            </div>
          </div>
        </div>
        <Footer />
      </div>
    </div>
  )
}

export default GettingStarted
