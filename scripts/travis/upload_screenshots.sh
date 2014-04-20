for screenshot in /tmp/*.png
do
    travis-artifacts upload --path "$screenshot"
done
for screenshot in /tmp/*.html
do
    travis-artifacts upload --path "$screenshot"
done
for screenshot in /tmp/*.log
do
    travis-artifacts upload --path "$screenshot"
done
tar -cvzf /tmp/task_data.tar.gz task_data
travis-artifacts upload --path /tmp/task_data.tar.gz
tar -cvzf /tmp/database.tar.gz db.sqlite3
travis-artifacts upload --path /tmp/database.tar.gz
