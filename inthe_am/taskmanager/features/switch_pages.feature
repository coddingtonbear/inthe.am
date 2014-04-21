Feature: User can navigate between pages

    Scenario: User can navigate to Sync page
        Given the user is logged-in
        When the user clicks the link "Sync"
        Then the page contains the heading "Synchronizing with Taskwarrior"

    Scenario: User can navigate to SMS page
        Given the user is logged-in
        When the user clicks the link "SMS"
        Then the page contains the heading "Adding tasks via SMS"

    Scenario: User can navigate to API page
        Given the user is logged-in
        When the user clicks the link "API"
        Then the page contains the heading "API Key"

    Scenario: User can navigate to Log page
        Given the user is logged-in
        When the user clicks the link "Log"
        Then the page contains the heading "Activity Log"

    Scenario: User can navigate to Settings page
        Given the user is logged-in
        When the user clicks the link "Settings"
        Then the page contains the heading "Settings"
