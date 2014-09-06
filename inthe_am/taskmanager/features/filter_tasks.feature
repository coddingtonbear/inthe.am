Feature: User can filter task list to show only requested tasks

    Scenario: User can filter to show tasks by project.
        Given the user is logged-in
        And a task with the following details exists
            | Key         | Value       |
            | description | "Alpha"     |
            | project     | "MyProject" |
        And a task with the following details exists
            | Key | Value |
            | description | "Beta" |
            | project | "NotMyProject" |
        And a task with the following details exists
            | Key | Value | 
            | description | "Delta" |
        When the user clicks the link "Tasks"
        And the filter "project:MyProject" is supplied
        Then a task with the description "Alpha" is visible in the sidebar
        And a task with the description "Beta" is not visible in the sidebar
        And a task with the description "Delta" is not visible in the sidebar

    Scenario: User can filter to show tasks by tag.
        Given the user is logged-in
        And a task with the following details exists
            | Key         | Value      |
            | description | "Alpha"    |
            | tags        | ["my_tag"] |
        And a task with the following details exists
            | Key         | Value          |
            | description | "Beta"         |
            | tags        | ["not_my_tag"] |
        And a task with the following details exists
            | Key         | Value                    |
            | description | "Delta"                  |
            | tags        | ["not_my_tag", "my_tag"] |
        When the user clicks the link "Tasks"
        And the filter "+my_tag" is supplied
        Then a task with the description "Alpha" is visible in the sidebar
        And a task with the description "Beta" is not visible in the sidebar
        And a task with the description "Delta" is visible in the sidebar
