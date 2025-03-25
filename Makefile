main:
	python -m uvicorn main:app --reload
install:
	pip install -r requirements.txt

git:
	git add .
	git commit -m "$(m)"
	git push

gen-grpc:
	python -m grpc_tools.protoc -Igrpc/services=protos \
	--python_out=. --grpc_python_out=. \
	--pyi_out=. \
	$(shell find protos -name "*.proto")  
	
