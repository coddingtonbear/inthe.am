tar -czf /tmp/testing_artifacts.tar.gz --exclude '*.tar.gz' /tmp
travis-artifacts upload --path /tmp/testing_artifacts.tar.gz
tar -czf /tmp/task_data.tar.gz task_data
travis-artifacts upload --path /tmp/task_data.tar.gz
