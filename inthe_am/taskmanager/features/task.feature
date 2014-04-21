Feature: User can manipulate tasks

    Scenario: User can create a task
        Given the user is logged-in
        When the user clicks the link "New"
        And the user waits for 1 seconds
        And the user enters the text "Test" into the field named "description"
        And the user clicks the button labeled "Save"
        And the user waits for 1 seconds
        Then a task with the description "Test" will exist

    Scenario: User can view existing task
        Given the user is viewing an existing task with the description "Alpha"
        When the user accesses the url "/"
        Then a task named "Alpha" is visible in the task list
        And a task named "Alpha" is the opened task

    @wip
    Scenario: User's view switches to new task upon creation
        Given the user is viewing an existing task with the description "Alpha"
        When the user accesses the url "/"
        And the user creates a new task with the description "Beta"
        And the user waits for 2 seconds
        Then a task named "Beta" is the opened task
