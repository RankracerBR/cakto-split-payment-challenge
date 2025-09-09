## Build images without cache
build:
	docker compose build

## Start containers in detached mode (builds changed ones automatically)
up:
	docker compose up -d

## Start and rebuild everything (useful after changes to Dockerfile or dependencies)
rebuild: 
	docker compose up -d --build --force-recreate

## Rebuild and restart only backend service (no dependency services restarted)
# Usage: make restart service=backend
restart:
	docker compose build $(service)
	docker compose up -d --build --force-recreate --no-deps $(service)

## Stop and remove containers, networks, and volumes
down:
	docker compose down -v

## Stop only
stop:
	docker compose down