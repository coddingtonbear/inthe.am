import React, {FunctionComponent} from 'react'
import {Button, Callout, Colors} from 'react-foundation'
import {useSelector} from 'react-redux'
import request from '../clients/request'
import {useToasts} from 'react-toast-notifications'
import {push} from 'connected-react-router'

import {RootState, useAppDispatch} from '../store'
import Footer from './Footer'
import {refreshStatus} from '../thunks/status'

const PrivacyPolicy: FunctionComponent = () => {
  const mustAccept = useSelector((state: RootState) =>
    state.status.logged_in ? !state.status.privacy_policy_up_to_date : false
  )
  const acceptUrl = useSelector(
    (state: RootState) =>
      state.status.logged_in && state.status.urls?.privacy_policy_accept
  )
  const {addToast} = useToasts()
  const dispatch = useAppDispatch()

  function acceptTerms() {
    if (!acceptUrl) {
      throw Error('No privacy policy acceptance URL found')
    }

    const formData = new FormData()
    formData.set('version', '1')

    request('POST', acceptUrl, {
      data: formData,
      lookupApiUrl: false,
    }).then(() => {
      addToast('Privacy policy accepted.', {appearance: 'success'})
      dispatch(refreshStatus()).then(() => {
        dispatch(push('/tasks'))
      })
    })
  }

  return (
    <div className="row standalone">
      <div className="standalone-content">
        <h2>Our Privacy Policy</h2>
        {mustAccept && (
          <Callout color={Colors.ALERT}>
            You must press the 'Accept' button below to continue.
          </Callout>
        )}

        <h3 id="what-this-policy-covers">What this policy covers</h3>
        <p>
          Inthe.AM (“we”, “us”, “I”, “me”) is a side project of a programmer who
          builds tools (like this website) for the joy of making things — we
          don’t want any more of your data than we absolutely need, but are
          committed to your privacy for the information that we do collect. We
          believe that it is important for you to understand how your
          information is being used, and this policy is intended to help you
          understand:
        </p>
        <ul>
          <li>What types of information we collect</li>
          <li>How we use the information we collect</li>
          <li>How we share the information we collect</li>
          <li>How we store and secure the information we collect</li>
          <li>How to access and control the information we collect</li>
          <li>What our policy towards children is</li>
        </ul>
        <p>
          This Privacy Policy covers the data you share with us via Inthe.AM or
          any integrations you enable for your account.{' '}
          <strong>
            If you do not agree with this policy, do not access or use our
            services
          </strong>
          .
        </p>
        <h3 id="types-of-information-collected">
          Types of Information Collected
        </h3>
        <ul>
          <li>
            Information you provide to us
            <ul>
              <li>
                We collect task information that you provide to us via the
                website, an integration like E-mail, SMS, the REST API, or by
                synchronizing your Taskwarrior client with Inthe.AM.
              </li>
            </ul>
          </li>
          <li>
            Information we collect automatically
            <ul>
              <li>
                Your use of the service
                <ul>
                  <li>We keep track of the features you use.</li>
                  <li>
                    We keep track of changes you make to your task lists for the
                    purposes of updating your task list and interacting with any
                    integrations you have enabled.
                  </li>
                </ul>
              </li>
              <li>
                We record logs documenting task interactions, synchronizations,
                and errors.
              </li>
              <li>We record the device you use for accessing the site.</li>
              <li>
                We store cookies so we can keep track of the fact that you are
                logged-in.
              </li>
              <li>
                We collect anonymous usage information on visitors through the
                use of Google Analytics, and they may themselves use third-party
                cookies for tracking sessions.
              </li>
            </ul>
          </li>
          <li>
            Information we receive from other sources
            <ul>
              <li>
                We collect your name and e-mail address from Google as part of
                the log-in process.
              </li>
              <li>
                We allow you to configure integrations with third-party systems
                to allow you other ways of managing your task list, and may
                collect task data from those services.
              </li>
            </ul>
          </li>
        </ul>
        <h3 id="how-we-use-information-we-collect">
          How we use information we collect
        </h3>
        <ul>
          <li>
            To provide you with a way of accessing your tasks: This use of your
            information should, hopefully, not be a surprise.
          </li>
          <li>
            For research and development: We use information we collect about
            which features are used as a way of identifying which features to
            discontinue, which features to allocate limited resources to, as
            well as to develop new feature ideas.
          </li>
          <li>
            To communicate with you: We use information we collect so we can
            reach out to you if a problem with your account occurs, or, in very
            rare situations, just to say hello.
          </li>
          <li>
            For support: We use your account information to answer your
            questions, should you have any.
          </li>
        </ul>
        <h3 id="how-we-share-information-we-collect">
          How we share information we collect
        </h3>
        <ul>
          <li>We do not sell any personal information to third parties.</li>
          <li>
            We may disclose personal information to third parties in order to
            provide services you have requested. This is relevant for the Trello
            integration we offer in that your task information is sent to Trello
            as a part of enabling the integration.
          </li>
          <li>
            With your consent: If you would like a copy of your data, you can
            ask for it by reaching out to privacy@inthe.am.
          </li>
          <li>
            In compliance with legal obligations: We may record, use, or
            disclose your personal data if necessary to comply with a law,
            regulation, legal process, or governmental request.
          </li>
        </ul>
        <h3 id="how-we-store-and-secure-information-we-collect">
          How we store and secure information we collect
        </h3>
        <ul>
          <li>
            How we store information
            <ul>
              <li>Inthe.AM’s servers are located in the United States.</li>
              <li>
                In addition to other reasonable technical security measures
                including firewalls, we use industry standard SSL-encrypted
                connections for all web traffic.
              </li>
              <li>
                Your task list is encrypted during transfer, and stored on an
                encrypted volume while at rest.
              </li>
              <li>
                Although technical measures are in place for preventing
                unauthorized access to your stored task information, no security
                measures are perfect, and due to the inherent nature of the
                internet, we cannot guarantee that your data is absolutely safe.
              </li>
            </ul>
          </li>
          <li>
            How long we keep information
            <ul>
              <li>
                Account information: until you delete your account or up to 13
                months after your last activity.
              </li>
              <li>
                Information you share: until you delete your account or up to 13
                months after your last activity.
              </li>
            </ul>
          </li>
        </ul>
        <h3 id="how-to-access-and-control-your-information">
          How to access and control your information
        </h3>
        <ul>
          <li>
            Access and update your information:
            <ul>
              <li>
                You have complete control over your stored task information
                using either the site itself or one of your enabled
                integrations.
              </li>
              <li>
                If you would like to update the e-mail address or name that we
                have on file for you, you can contact us at privacy@inthe.am.
              </li>
            </ul>
          </li>
          <li>
            Delete your information:
            <ul>
              <li>
                You can delete stored task data by using the features available
                on the site.
              </li>
              <li>
                You can contact privacy@inthe.am to delete your account
                entirely.
              </li>
            </ul>
          </li>
        </ul>
        <h3 id="regarding-children">Regarding Children</h3>
        <ul>
          <li>
            You may not use our service if you are under the age of 16. If an
            account is found to have been created by a person under the age of
            16, we will take steps to delete their account.
          </li>
        </ul>

        {mustAccept && (
          <Button onClick={acceptTerms} id="accept-terms">
            Accept
          </Button>
        )}
        <Footer />
      </div>
    </div>
  )
}

export default PrivacyPolicy
