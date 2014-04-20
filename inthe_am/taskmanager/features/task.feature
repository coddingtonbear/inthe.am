Feature: User can manipulate tasks

    Scenario: User can create a task
        Given the user is logged-in
        When the user clicks the link "New"
        And the user waits for 1 seconds
        And the user enters the text "Test" into the field named "description"
        And the user clicks the button labeled "Save"
        And the user waits for 1 seconds
        Then a task with the description "Test" will exist
