tar -czf /tmp/testing_artifacts.tar.gz --exclude '*.tar.gz'
travis-artifacts upload --path /tmp/testing_artifacts.tar.gz
tar -czf /tmp/task_data.tar.gz task_data
travis-artifacts upload --path /tmp/task_data.tar.gz
tar -czf /tmp/database.tar.gz db.sqlite3
travis-artifacts upload --path /tmp/database.tar.gz
