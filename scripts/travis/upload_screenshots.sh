tar -cvzf /tmp/testing_artifacts.tar.gz /tmp/*.log /tmp/*.html /tmp/*.png
travis-artifacts upload --path /tmp/testing_artifacts.tar.gz
tar -cvzf /tmp/task_data.tar.gz task_data
travis-artifacts upload --path /tmp/task_data.tar.gz
tar -cvzf /tmp/database.tar.gz db.sqlite3
travis-artifacts upload --path /tmp/database.tar.gz
