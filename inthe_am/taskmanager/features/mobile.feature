Feature: Alterations to normal user experience on mobile.

    Scenario: User is presented with a promo when accessing site.
        Given the user is using a mobile device
        And the test account user does not exist
        When the user accesses the url "/"
        Then the page contains the heading "Inthe.AM"

    Scenario: User is redirected to tasks when logging-in.
        Given the user is using a mobile device
        And the user is logged-in
        When the user accesses the url "/"
        Then the page will transition to "/getting-started"
