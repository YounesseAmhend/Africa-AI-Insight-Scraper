main:
	uvicorn main:app --reload
install:
	pip install -r requirements.txt

git:
	git add .
	git commit -m "$(m)"
	git push