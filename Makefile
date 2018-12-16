build:
	docker build -f worker/Dockerfile . -t worker
run:
	FLASK_DEBUG=1 flask run
