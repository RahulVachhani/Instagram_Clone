#!/bin/bash

python3 manage.py makemigrations --dry-run --check
STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo "❌ Uncommitted migrations found! Run 'python3 manage.py makemigrations'."
  exit 1
fi

echo "✅ Migrations are up-to-date!"
exit 0
