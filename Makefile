default: build

up:
	docker-compose up -d --remove-orphans

build:
	docker-compose up --build -d --remove-orphans

down:
	docker-compose down
	rm -rf ./src/collector/common/
	rm -rf ./src/generator/common/
	rm -rf ./src/dash/common/

clean:
	docker volume rm the-trains_mongo-volume

k8s_setup:
	kubectl apply -f ./k8s/setup.yaml

k8s_deploy:
	skaffold run -f ./k8s/skaffold.yaml

k8s_delete:
	skaffold delete -f ./k8s/skaffold.yaml
	kubectl delete -f ./k8s/setup.yaml

test:
	pytest .

jupyter:
	jupyter-lab --ip=0.0.0.0 --allow-root --port 8891