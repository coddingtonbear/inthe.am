Feature: User can navigate between pages

    @wip
    Scenario: User can navigate to Sync page
        Given the user is logged-in
        When the user clicks the link "Sync"
        Then the page contains the heading "Synchronizing with Taskwarrior"

    @wip
    Scenario: User can navigate to Sync page
        Given the user is logged-in
        When the user clicks the link "SMS"
        Then the page contains the heading "Adding tasks via SMS"

    @wip
    Scenario: User can navigate to Sync page
        Given the user is logged-in
        When the user clicks the link "API"
        Then the page contains the heading "API Key"

    @wip
    Scenario: User can navigate to Sync page
        Given the user is logged-in
        When the user clicks the link "Log"
        Then the page contains the heading "Activity Log"

    @wip
    Scenario: User can navigate to Sync page
        Given the user is logged-in
        When the user clicks the link "Settings"
        Then the page contains the heading "Settings"
