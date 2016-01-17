travis-artifacts upload --path /tmp/task_2.3.0-1*.deb
travis-artifacts upload --path /tmp/taskd_1.0.0-1*.deb
sudo rm /tmp/*.deb
sudo rm -rf /tmp/pip_cache
sudo rm -rf /tmp/npm-*
sudo rm -rf /tmp/async-disk-cache
sudo rm -rf /tmp/root
sudo rm -rf /tmp/twweb
tar -czf /tmp/testing_artifacts.tar.gz --exclude '*.tar.gz' /tmp
travis-artifacts upload --path /tmp/testing_artifacts.tar.gz
tar -czf /tmp/task_data.tar.gz task_data
travis-artifacts upload --path /tmp/task_data.tar.gz
