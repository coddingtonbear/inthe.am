Feature: Duplicate recurring tasks are merged/mergeable.

    Scenario: Duplicated task is merged
        Given a task "alpha" with the following details
             | Key         | Value                    | 
             | description | "This is the main task." | 
        Given a task "beta" with the following details
             | Key         | Value                   | 
             | description | "This is the duplicate" | 
        When the tasks "alpha" and "beta" are merged
        Then task "beta" will be annotated as a duplicate of "alpha"
