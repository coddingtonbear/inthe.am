Feature: User can view task UDA details

    @wip
    Scenario: User can view task having specified UDAs
        Given the user is logged-in
        And the user has the following custom configuration
            """
            uda.favoritenumber.type=string
            uda.favoritenumber.label=User Username
            uda.thankscount.type=numeric
            uda.thankscount.label=Thanked
            uda.encouraged.type=date
            uda.encouraged.label=Encouragement Date
            """
        And a task with the following details exists
            | Key            | Value              |
            | description    | "Delta"            |
            | favoritenumber | "One"              |
            | thankscount    | 24                 |
            | encouraged     | "20100405T140000Z" |
        When the user accesses the url "/"
        Then a task named "Delta" is visible in the task list
        And a task named "Delta" is the opened task
        And the following values are visible in the task's details
            | Key                | Value      |
            | Description        | Delta      |
            | User Username      | One        |
            | Thanked            | 24         |
            | Encouragement Date | 04/05/2010 |
