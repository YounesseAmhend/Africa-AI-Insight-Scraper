install:
	pip install -r requirements.txt

git:
	git add .
	git commit -m "$(m)"
	git push

gen-grpc:
	python -m grpc_tools.protoc -I. \
		--python_out=. --grpc_python_out=. \
		--pyi_out=. \
		$(shell find protos -name "*.proto")  

client:
	python grpc_client.py
	

server:
	make run


build:
	docker build . -t scraper

run:
	docker run -p 50051:50051 scraper

delete-build:
	docker rmi -f scraper

docker:
	make delete-build && make build && make run

slim-prepare:
	docker create -v /dcert_path --name dcert alpine:latest /bin/true
	docker cp $DDOCKER_CERT_PATH/. dcert:/dcert_path

slim:
	docker run --rm --volumes-from dcert \
		-e DOCKER_HOST=$DDOCKER_HOST \
		-e DOCKER_TLS_VERIFY=$DOCKER_TLS_VERIFY \
		-e DOCKER_CERT_PATH=/dcert_path \
		dslim/slim build scraper

slim-run:
	docker run -p 50051:50051 scraper.slim

submodule:
	git submodule update --init --recursive