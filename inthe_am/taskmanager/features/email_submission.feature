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
            To: 3e196d2f-6947-42e5-8134-b954860c2c9c__project=biscuit__priority=L@inthe.am
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

    Scenario: User can receive non-ascii task via e-mail
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
            Content-Type: multipart/alternative; boundary="576bd179_18a892d5_a7b9"

            --576bd179_18a892d5_a7b9
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: quoted-printable
            Content-Disposition: inline

            =E3=81=82

            --576bd179_18a892d5_a7b9
            Content-Type: text/html; charset="utf-8"
            Content-Transfer-Encoding: quoted-printable
            Content-Disposition: inline

            <html><head><style>body=7Bfont-family:Helvetica,Arial;font-size:13px=7D</=
            style></head><body style=3D=22word-wrap: break-word; -webkit-nbsp-mode: s=
            pace; -webkit-line-break: after-white-space;=22><div id=3D=22bloop=5Fcust=
            omfont=22 style=3D=22font-family:Helvetica,Arial;font-size:13px; color: r=
            gba(0,0,0,1.0); margin: 0px; line-height: auto;=22>=E3=81=82</div><div id=
            =3D=22bloop=5Fsign=5F1466683757734444032=22 class=3D=22bloop=5Fsign=22><d=
            iv class=3D=22bloop=5Foriginal=5Fhtml=22>


            </div><div class=3D=22bloop=5Fmarkdown=22><p></p></div></div></body></htm=
            l>
            --576bd179_18a892d5_a7b9--
            """
        Then a single pending task with the following details will exist
            | Key         | Value |
            | description | "あ"  |
