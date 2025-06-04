#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

if [[ -n "$CREATE_SUPERUSER" ]]; then
  python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || true
  echo "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME')
user.set_password('$DJANGO_SUPERUSER_PASSWORD')
user.save()
" | python manage.py shell
fi

