Feature: User can receive incoming tasks via e-mail

    @wip
    Scenario: User can receive task via e-mail
        Given the user is logged-in
        And the user's task store is configured with the following options
            | Key       | Value    |
            | secret_id | "secret" |
        When the following incoming email is processed
            """
            From: alpha
            To: secret@inthe.am
            Subject: New

            priority:H This is an important task +important project:alpha
            """
        Then a single pending task with the following details will exist
            | Key         | Value                       |
            | description | "This is an important task" |
            | tags        | ["important"]               |
            | priority    | "H"                         |
            | project     | "alpha"                     |
