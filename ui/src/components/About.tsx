import React, {FunctionComponent} from 'react'

import Footer from './Footer'
import Icon from './Icon'

export const About: FunctionComponent = () => {
  return (
    <div className="row standalone homepage">
      <div className="standalone-content">
        <img id="about_logo" src="/assets/about_logo.svg" />
        <h1>Inthe.AM</h1>
        <div className="medium-12">
          <p className="tagline">
            Access your <a href="http://taskwarrior.org/">Taskwarrior</a>
            &nbsp;task list from wherever you happen to be.
          </p>
        </div>
        <div>
          <a href="/login/google-oauth2/" className="button radius">
            Log In with Google to get started
          </a>
        </div>
        <div className="medium-12">
          <img src="/assets/web_ui.png" />
        </div>
        <div className="medium-12 features">
          <div className="promo_cell">
            <Icon name="refresh" />
            <p>
              <span className="headline">Built-In Taskserver</span>
              We've built in an automatically-configured synchronization server
              that you can set up your local Taskwarrior client to synchronize
              with.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="mail" />
            <p>
              <span className="headline">E-mail</span>
              You can easily add tasks to your task list by sending an e-mail to
              your own whitelist-controlled e-mail address.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="rss" />
            <p>
              <span className="headline">RSS Feeds</span>
              You can use the provided RSS feed functionality to display your
              tasks in any RSS reader.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="arrows-out" />
            <p>
              <span className="headline">Trello Integration</span>
              Ever wanted to use a Trello or kanban with your Taskwarrior tasks?
              By using Inthe.AM's Trello integration you can start today.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="calendar" />
            <p>
              <span className="headline">iCal Feed</span>
              Want an easy way for you to see what tasks are due today in Google
              Calendar? Inthe.AM gives you an iCalendar feed allowing you to do
              that.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="mobile" />
            <p>
              <span className="headline">SMS</span>
              Have you ever wanted to quickly add a task to your task list while
              on-the-go? Using Inthe.AM's Twilio integration, you can add tasks
              by sending an SMS message.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="cloud" />
            <p>
              <span className="headline">Mobile-ready web UI</span>
              Inthe.AM is mobile-ready, and looks just about as good on small
              screens as it does on your desktop. There's even a web-app mode
              usable for those of you with an iphone.
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="lightbulb" />
            <p>
              <span className="headline">Open Source</span>
              Inthe.AM is an open-source application relying upon open-source
              libraries. The features you want are just a pull-request or a{' '}
              <a href="https://github.com/coddingtonbear/inthe.am/issues?page=1&state=open">
                bug-report
              </a>{' '}
              away!
            </p>
          </div>
          <div className="promo_cell">
            <Icon name="widget" />
            <p>
              <span className="headline">RESTful API</span>
              You can write your own tools for creating, reading, changing,
              completing, or deleting your tasks using our built-in RESTful API.
            </p>
          </div>
        </div>
        <Footer />
      </div>
    </div>
  )
}

export default About
