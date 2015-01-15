Feature: User can navigate between pages

    Scenario: User can navigate to Log page
        Given the user is logged-in
        When the user clicks the link "Log"
        Then the page contains the heading "Activity Log"

    Scenario: User can navigate to Settings page
        Given the user is logged-in
        When the user clicks the link "Configuration"
        Then the page contains the heading "Configuration & Settings"
