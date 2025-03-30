main:
	python -m uvicorn main:app --reload
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
	python app.py


build:
	docker build . -t scraper

run-build:
	docker run -p 50051:50051 scraper

delete-build:
	docker rmi -f scraper

docker:
	make delete-build && make build && make run-build