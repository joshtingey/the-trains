dev:
	docker-compose up --build -d

down:
	docker-compose down

prod_setup:
	kubectl apply -f manifests/setup/

prod_build:
	sudo skaffold build

prod_deploy:
	kubectl apply -f manifests/mongo/
	kubectl apply -f manifests/collector/
	kubectl apply -f manifests/thetrains/

clean:
	docker system prune -a --volumes