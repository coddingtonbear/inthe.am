echo "Starting..."
source scripts/vagrant/environment_variables.sh
echo "Sourced environment variables."
python manage.py runtests
echo "Finished."
