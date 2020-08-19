up:
	docker-compose up --build -d --remove-orphans

down:
	docker-compose down
	rm -rf ./src/collector/common/
	rm -rf ./src/generator/common/
	rm -rf ./src/dash/common/

k8s:
	kubectl apply -f ./k8s/setup.yaml

deploy:
	skaffold run -f ./k8s/skaffold.yaml

test:
	docker build -t thetrains-test -f ./tests/Dockerfile .
	docker run thetrains-test