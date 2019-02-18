Feature: Integration tests
    In order to run integration tests
    We'll spin up a Cassandra cluster

    Scenario: Run a nodetool status command
        Given I run "nodetool status" on the cluster with strategy "all"
        Then there are 9 nodes reported by nodetool
        And there are no errors in the job

    Scenario: Run a nodetool command that doesnt exist
        Given I run "nodetool statussss" on the cluster with strategy "all"
        Then the job fails