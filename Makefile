.PHONY: env up down logs ps doctor

env:
	bash scripts/bootstrap_env.sh

up: env
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=120

ps:
	docker compose ps

doctor:
	docker info
	docker compose config --quiet
