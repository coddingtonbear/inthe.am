import React, {FunctionComponent} from 'react'

import SyncInstructions from '../SyncInstructions'

const Synchronization: FunctionComponent = () => {
  return (
    <div id="custom_taskd" className="content">
      <div className="row">
        <div className="large-12 columns">
          <h3>Synchronization</h3>
          <p>
            Inthe.AM provides a built-in taskserver for you to synchronize your
            tasks with; follow the instructions below for setting up your local
            taskwarrior client to synchronize with Inthe.AM.
          </p>
        </div>
      </div>
      <div className="row">
        <div className="large-12 columns">
          <SyncInstructions />
        </div>
      </div>
    </div>
  )
}

export default Synchronization
