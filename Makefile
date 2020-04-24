mongo_up:
	sed -i "s/ENV=.*/ENV=local/g" .env
	source ./deploy/local_mongo.sh

mongo_down:
	sed -i "s/ENV=.*/ENV=local/g" .env
	docker stop mongo
	docker container rm mongo

docker_up:
	sed -i "s/ENV=.*/ENV=docker/g" .env
	docker-compose up --build -d

docker_down:
	sed -i "s/ENV=.*/ENV=docker/g" .env
	docker-compose down

prod_build:
	sed -i "s/ENV=.*/ENV=prod/g" .env
	sudo skaffold build -f ./deploy/skaffold.yaml

prod_deploy:
	sed -i "s/ENV=.*/ENV=prod/g" .env
	./deploy/deploy.sh

clean:
	docker system prune -a --volumes