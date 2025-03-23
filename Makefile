main:
	python -m uvicorn main:app 
install:
	pip install -r requirements.txt

git:
	git add .
	git commit -m "$(m)"
	git push

llm:
	python llm.py