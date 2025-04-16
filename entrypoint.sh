#!/bin/sh

# Print the variables to debug
echo "Checking PostgreSQL at $DB_HOSTNAME:$DB_PORT"

# Wait for postgres with proper error handling and timeout
echo 'Waiting for postgres...'
count=0
max_tries=30
until nc -z $DB_HOSTNAME $DB_PORT || [ $count -gt $max_tries ]; do
    echo "Waiting for PostgreSQL ($count/$max_tries)..."
    sleep 1
    count=$((count+1))
done

if [ $count -gt $max_tries ]; then
    echo "Error: PostgreSQL did not start in time!"
    exit 1
fi

echo 'PostgreSQL started'

echo 'Running migrations...'
python manage.py migrate

echo 'Collecting static files...'
python manage.py collectstatic --no-input

# Execute the command passed to the script
exec "$@"