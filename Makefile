build:
	docker build -f worker/Dockerfile . -t worker
run:
	docker run -p 127.0.0.1:6000:6000 -d worker
	FLASK_DEBUG=1 flask run --host=0.0.0.0
