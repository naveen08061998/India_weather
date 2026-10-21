web: pip install -q -r requirements-web.txt && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
current-affairs: pip install -q -r requirements-web.txt && gunicorn current_affairs.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
railways: pip install -q -r requirements-web.txt && gunicorn indian_railways.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
stock-market: pip install -q -r requirements-web.txt && gunicorn stock_market.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
air-quality: pip install -q -r requirements-web.txt && gunicorn air_quality.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
gov-updates: pip install -q -r requirements-web.txt && gunicorn gov_updates.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
short-news: pip install -q -r requirements-web.txt && gunicorn short_news.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
