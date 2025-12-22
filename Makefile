# virtual environment commands
venv-create:
	python3 -m venv venv

venv-up:
	source venv/bin/activate

venv-down:
	deactivate

# python commands
install-pip:
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade

freeze-pip:
	pip freeze > requirements.txt

# tests commands
run-tests:
	pytest tests --disable-warnings

# fastapi commands
run-fastapi:
	uvicorn main:app --reload

# docker commands
build-docker:
	docker build -t xml-to-json-api .

run-docker:
	docker run -d -p 8000:8000 --name xml-to-json-api xml-to-json-api

stop-docker:
	docker stop xml-to-json-api
	docker rm xml-to-json-api

# cloudrun commands
deploy-cloudrun:
	gcloud run deploy timestamp-api \
		--image us-central1-docker.pkg.dev/project-c81c4edd-4dfa-4b1c-bf8/timestamp-api/api \
		--region us-central1 \
		--set-env-vars API_KEY=<your_api_key_here> \
		--memory 256Mi \
		--cpu 1 \
		--max-instances 1 \
		--timeout 60 \
		--allow-unauthenticated