import React, {FunctionComponent} from 'react'

export const Footer: FunctionComponent = () => {
  return (
    <div id="footer">
      <hr />
      Lovingly crafted by{' '}
      <a href="http://github.com/coddingtonbear">Adam Coddington</a> and others.
      See our <a href="/privacy-policy">Privacy Policy</a> and{' '}
      <a href="/terms-of-service">Terms of Service</a>.
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
