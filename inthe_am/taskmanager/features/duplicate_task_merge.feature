Feature: Duplicate recurring tasks are merged/mergeable.

    Scenario: Duplicated tasks can be found and merged en masse
        Given a task "alpha" with the following details
             | Key         | Value                                  | 
             | description | "Some task"                            | 
             | parent      | "edcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 10                                     | 
        Given a task "beta" with the following details
             | Key         | Value                                  | 
             | description | "Some task (duplicate)"                | 
             | parent      | "edcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 10                                     | 
        Given a task "gamma" with the following details
             | Key         | Value                                  | 
             | description | "Some task (not a duplicate)"          | 
             | parent      | "edcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 11                                     | 
        Given a task "epsilon" with the following details
             | Key         | Value                                  | 
             | description | "Some task (also not a duplicate)"     | 
             | parent      | "fdcc89e7-0ea7-4455-bb0d-4a088007b844" | 
             | imask       | 10                                     | 
        When I search for duplicate tasks
        Then task "alpha" and task "beta" are found as duplicates
        When I merge duplicate tasks
        Then task "beta"'s "status" field is set to "deleted"
        And the task "beta" will be marked as a duplicate of "alpha"

    Scenario: Duplicated tasks can be found and merged individually
        Given a task "alpha" with the following details
             | Key         | Value                                  | 
             | description | "Some task"                            | 
             | parent      | "edcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 12                                     | 
        Given a task "beta" with the following details
             | Key         | Value                                  | 
             | description | "Some task (duplicate)"                | 
             | parent      | "edcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 12                                     | 
        Given a task "gamma" with the following details
             | Key         | Value                                  | 
             | description | "Some task (not a duplicate)"          | 
             | parent      | "fdcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 12                                     | 
        Given a task "epsilon" with the following details
             | Key         | Value                                  | 
             | description | "Some task (also not a duplicate)"     | 
             | parent      | "edcc89e7-0ea7-4455-bb0d-4a088007b845" | 
             | imask       | 13                                     | 
        When I search for duplicates of task "beta"
        Then the task I searched for duplicates of is found to be a duplicate of "alpha"
        When I check for duplicate tasks of "beta"
        Then task "beta"'s "status" field is set to "deleted"
        And the task "beta" will be marked as a duplicate of "alpha"
