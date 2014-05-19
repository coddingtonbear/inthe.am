Feature: User can manipulate tasks

    Scenario: User can create a basic task
        Given the user is logged-in
        When the user clicks the link "New"
        And the user waits for 1 seconds
        And the user enters the text "Test" into the field named "description"
        And the user clicks the button labeled "Save"
        And the user waits for 1 seconds
        Then a task with the description "Test" will exist

    Scenario: User can create a task with taskwarrior details
        Given the user is logged-in
        When the user clicks the link "New"
        And the user waits for 1 seconds
        And the user enters the text "My Description" into the field named "description"
        And the user enters the text "Alpha" into the field named "project"
        And the user selects the option "L" from the field named "priority"
        And the user enters the text "Magic" into the field named "tags"
        And the user enters the text "2020-03-02 12:00" into the field named "due"
        And the user enters the text "2019-03-02 12:00" into the field named "scheduled"
        And the user enters the text "2018-03-02 12:00" into the field named "wait"
        And the user clicks the button labeled "Save"
        And the user waits for 1 seconds
        Then a single waiting task with the following details will exist
            | Key         | Value              |
            | description | "My Description"   |
            | project     | "Alpha"            |
            | priority    | "L"                |
            | tags        | ["Magic"]          |
            | due         | "20200302T120000Z" |
            | scheduled   | "20190302T120000Z" |
            | wait        | "20180302T120000Z" |

    Scenario: User can view existing task
        Given the user is viewing an existing task with the description "Alpha"
        When the user accesses the url "/"
        Then a task named "Alpha" is visible in the task list
        And a task named "Alpha" is the opened task

    Scenario: User's view switches to new task upon creation
        Given the user is viewing an existing task with the description "Alpha"
        When the user accesses the url "/"
        And the user creates a new task with the description "Beta"
        Then a task named "Beta" is the opened task

    Scenario: User can update existing task
        Given the user is viewing an existing task with the description "Alpha"
        When the user accesses the url "/"
        And the user clicks the link "Edit"
        And the user waits for 1 seconds
        And the user clears the text field named "description"
        And the user enters the text "Beta" into the field named "description"
        And the user clicks the button labeled "Save"
        And the user waits for 1 seconds
        Then a single pending task with the following details will exist
            | Key         | Value  |
            | description | "Beta" |
