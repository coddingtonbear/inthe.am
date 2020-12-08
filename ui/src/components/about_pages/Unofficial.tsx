import React, {FunctionComponent} from 'react'
import {Callout, Colors} from 'react-foundation'

export const Unofficial: FunctionComponent = () => {
  return (
    <>
      <h1>Unofficial Inthe.AM Installation</h1>
      <Callout color={Colors.PRIMARY}>
        <p>
          Creating an account is easy; just follow the following two steps and
          you'll be up-and-running in no time:
        </p>
        <ol>
          <li>
            First, enter the shell for the web node by running{' '}
            <pre>docker-compose exec web bash</pre>.
          </li>
          <li>
            Then, from the prompt you are shown after the above command, run the
            command to create a new superuser account with
            <pre>python manage.py createsuperuser</pre>.
          </li>
        </ol>
      </Callout>
      <div>
        <a href="/admin/login/?next=/" className="button radius">
          Log In as Admin
        </a>
      </div>
    </>
  )
}

export default Unofficial
