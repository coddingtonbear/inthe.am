sudo rm /tmp/*.deb
sudo rm -rf /tmp/pip_cache
sudo rm -rf /tmp/npm-*
sudo rm -rf /tmp/async-disk-cache
sudo rm -rf /tmp/root
sudo rm -rf /tmp/twweb
tar -czf /tmp/testing_artifacts.tar.gz --exclude '*.tar.gz' /tmp
tar -czf /tmp/task_data.tar.gz task_data
