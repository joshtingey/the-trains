mongo_up:
	sed -i "s/ENV=.*/ENV=local/g" .env
	./deploy/local_mongo.sh

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

test:
	black ./common/ --check
	black ./collector/ --check
	black ./thetrains/ --check
	black ./tests/ --check
	flake8 --max-line-length=99 ./common/
	flake8 --max-line-length=99 ./collector/
	flake8 --max-line-length=99 ./thetrains/
	flake8 --max-line-length=99 ./tests/
	pydocstyle ./common/
	pydocstyle ./collector/
	pydocstyle ./thetrains/
	pydocstyle ./tests/
	pytest

clean:
	docker system prune -a --volumes