#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Running database migrations..."
alembic upgrade head

echo "✨ Migrations complete! Starting the application..."
exec "$@"
