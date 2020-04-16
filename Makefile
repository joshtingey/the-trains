db: 
	docker-compose -f docker-compose.common.yml up --build -d

dev:
	docker-compose -f docker-compose.common.yml -f docker-compose.dev.yml up --build -d

prod:
	docker-compose -f docker-compose.common.yml -f docker-compose.prod.yml up --build -d

down:
	docker-compose -f docker-compose.common.yml -f docker-compose.dev.yml -f docker-compose.prod.yml down

clean:
	docker-compose down
	docker system prune -fa