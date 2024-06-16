.PHONY: up
up:
	docker compose up -d --build

.PHONY: down
down:
	docker compose down
	
.PHONY: interactive
interactive:
	docker compose run --rm app python /app/discussia/app.py interactive
	
.PHONE: help
help:
	docker compose run --rm app python /app/discussia/app.py --help

.PHONE: shell
shell:
	docker compose exec app bash