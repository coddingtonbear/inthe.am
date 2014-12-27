Feature: Alterations to normal user experience on mobile.

    Scenario: User is presented with a promo when accessing site from mobuile device.
        Given the user is using a mobile device
        And the test account user does not exist
        When the user accesses the url "/"
        Then the page contains the heading "Install Inthe.AM"

