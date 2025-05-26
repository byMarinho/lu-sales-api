sentry_migrations:
	docker-compose exec sentry sentry upgrade --noinput
	
sentry_create_user:
	docker-compose exec sentry sentry createuser --email admin@example.com --password 123@admin --superuser

migrations:
	docker-compose exec api uv pip install --system alembic
	docker-compose exec api uv run alembic upgrade head

migrations_create:
	docker-compose exec api uv run alembic revision --autogenerate -m "Added new migrations"

testes:
	docker-compose exec api env PYTHONPATH=/app uv run pytest -v --cov=app --cov-report=term-missing
