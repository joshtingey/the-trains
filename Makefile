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

k8s:
	kubectl apply -f ./k8s/setup.yaml

deploy:
	skaffold run -f ./k8s/skaffold.yaml

black:
	black src/ tests/

test:
	pytest --pydocstyle --flake8 --black -v -W ignore::pytest.PytestDeprecationWarning .

jupyter:
	jupyter-lab --ip=0.0.0.0 --allow-root --port 8890