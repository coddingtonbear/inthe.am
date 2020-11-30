import React, {FunctionComponent} from 'react'
import {Link} from 'react-router-dom'

export const Footer: FunctionComponent = () => {
  return (
    <div id="footer">
      <hr />
      Lovingly crafted by{' '}
      <a href="http://github.com/coddingtonbear">Adam Coddington</a> and others.
      See our <Link to="/privacy-policy">Privacy Policy</Link> and{' '}
      <Link to="/terms-of-service">Terms of Service</Link>.
      <br />
      Questions? Ask on{' '}
      <a href="https://gitter.im/coddingtonbear/inthe.am">Gitter</a>.
      <a href="http://github.com/coddingtonbear/inthe.am">
        Contribute to this project on Github
      </a>
      .
    </div>
  )
}

export default Footer
