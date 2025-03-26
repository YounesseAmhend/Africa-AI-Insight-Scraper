main:
	python -m uvicorn main:app --reload
install:
	pip install -r requirements.txt

git:
	git add .
	git commit -m "$(m)"
	git push

gen-grpc:
	python -m grpc_tools.protoc -I. --python_out=./rpc --grpc_python_out=./rpc --pyi_out=./rpc $(shell find protos -name "*.proto")

client:
	python grpc_client.py
	

server:
	python grpc_server.py
