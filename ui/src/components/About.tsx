import React, {FunctionComponent} from 'react'
import {useSelector} from 'react-redux'
import {Redirect} from 'react-router'

import {isOfficialServer} from '../utils/official'
import {RootState} from '../store'
import Footer from './Footer'
import Official from './about_pages/Official'
import Unofficial from './about_pages/Unofficial'

export const About: FunctionComponent = () => {
  const isLoggedIn = useSelector((state: RootState) => state.status.logged_in)

  if (isLoggedIn) {
    return <Redirect to="/tasks" />
  }
  if (isLoggedIn === null) {
    // We're still trying to figure out if we're logged in -- let's
    // let things settle before rendering anything
    return <></>
  }

  return (
    <div className="row standalone homepage">
      <div className="standalone-content">
        {isOfficialServer() ? <Official /> : <Unofficial />}
        <Footer />
      </div>
    </div>
  )
}

export default About
