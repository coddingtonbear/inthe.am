Feature: User can receive incoming tasks via e-mail

    @wip
    Scenario: User can receive task via e-mail
        Given the user is logged-in
        When an incoming task creation e-mail having the subject "New" and the following body is received
            """
            priority:h This is an important task +important project:alpha
            """
        Then a single pending task with the following details will exist
            | Key         | Value                       |
            | description | "This is an important task" |
            | tags        | ["important"]               |
            | priority    | "H"                         |
            | project     | "alpha"                     |
