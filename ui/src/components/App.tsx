import React from 'react'
import {BrowserRouter, Route, Switch, Redirect} from 'react-router-dom'

import About from './About'

const App = () => {
  return (
    <BrowserRouter>
      <Switch>
        <Route path="/about">
          <About />
        </Route>
        <Route path="/">
          <Redirect to="/about" />
        </Route>
      </Switch>
    </BrowserRouter>
  )
}

export default App
