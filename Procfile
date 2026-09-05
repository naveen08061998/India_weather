web: pip install -q -r requirements-web.txt && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
current-affairs: pip install -q -r requirements-web.txt && gunicorn current_affairs.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
railways: pip install -q -r requirements-web.txt && gunicorn indian_railways.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
