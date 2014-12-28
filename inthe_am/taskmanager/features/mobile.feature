Feature: Alterations to normal user experience on mobile.

    Scenario: User is presented with a promo when accessing site.
        Given the user is using a mobile device
        And the test account user does not exist
        When the user accesses the url "/"
        # Note that this is only true because this test is not being
        # ran on Inthe.AM itself.  What we're searching for is the
        # 'About' page.
        Then the page contains the heading "Local Installation"

    Scenario: User is redirected to tasks when logging-in.
        Given the user is using a mobile device
        And the user is logged-in
        When the user accesses the url "/"
        Then the page will transition to "/getting-started"
