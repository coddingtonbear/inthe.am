Feature: User can receive incoming tasks via e-mail

    Scenario: User can receive task via e-mail
        Given the user is logged-in
        And the user's task store is configured with the following options
            | Key             | Value                                  |
            | secret_id       | "3e196d2f-6947-42e5-8134-b954860c2c9c" |
            | email_whitelist | "*"                                    |
        When the following incoming email is processed
            """
            From: alpha
            To: 3e196d2f-6947-42e5-8134-b954860c2c9c@inthe.am
            Subject: New

            priority:H This is an important task +important project:alpha
            """
        Then a single pending task with the following details will exist
            | Key         | Value                       |
            | description | "This is an important task" |
            | tags        | ["important"]               |
            | priority    | "H"                         |
            | project     | "alpha"                     |

    Scenario: User can specify tags in "to" header
        Given the user is logged-in
        And the user's task store is configured with the following options
            | Key             | Value                                  |
            | secret_id       | "3e196d2f-6947-42e5-8134-b954860c2c9c" |
            | email_whitelist | "*"                                    |
        When the following incoming email is processed
            """
            From: alpha
            To: 3e196d2f-6947-42e5-8134-b954860c2c9c+important@inthe.am
            Subject: New

            Do something important
            """
        Then a single pending task with the following details will exist
            | Key         | Value                    |
            | description | "Do something important" |
            | tags        | ["important"]            |

    Scenario: User can specify field values in "to" header
        Given the user is logged-in
        And the user's task store is configured with the following options
            | Key             | Value                                  |
            | secret_id       | "3e196d2f-6947-42e5-8134-b954860c2c9c" |
            | email_whitelist | "*"                                    |
        When the following incoming email is processed
            """
            From: alpha
            To: 3e196d2f-6947-42e5-8134-b954860c2c9c__project=biscuit__priority=l@inthe.am
            Subject: New

            Do something important
            """
        Then a single pending task with the following details will exist
            | Key         | Value                    |
            | description | "Do something important" |
            | project     | "biscuit"                |
            | priority    | "L"                      |

    Scenario: E-mails from non-whitelisted addresses are rejected
        Given the user is logged-in
        And the user's task store is configured with the following options
            | Key             | Value                                  |
            | secret_id       | "3e196d2f-6947-42e5-8134-b954860c2c9c" |
            | email_whitelist | "beta"                                 |
        When the following incoming email is processed
            """
            From: alpha
            To: 3e196d2f-6947-42e5-8134-b954860c2c9c@inthe.am
            Subject: New

            priority:H This is an important task +important project:alpha
            """
        Then 0 pending tasks exist in the user's task list

    Scenario: Can receive task via e-mail having been forwarded
        Given the user is logged-in
        And the user's task store is configured with the following options
            | Key             | Value                                  |
            | secret_id       | "3e196d2f-6947-42e5-8134-b954860c2c9c" |
            | email_whitelist | "*"                                    |
        When the following incoming email is processed
            """
            From: alpha
            To: somewhere@myaccount.com
            Received: from somewhere.wherever.net([211.9.51.110])
                by eugene.adamcoddington.net with esmtp (Exim 4.76)
                (envelope-from <somewhere@somewhere.com>) id 1Y5ZxK-0007Wu-Kp
                for 3e196d2f-6947-42e5-8134-b954860c2c9c@inthe.am;
                Mon, 29 Dec 2014 13:01:54 +0000
            Subject: New

            Es muy importante.
            """
        Then a single pending task with the following details will exist
            | Key         | Value                       |
            | description | "Es muy importante."        |
