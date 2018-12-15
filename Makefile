build:
	docker build worker/ -t worker
run:
	FLASK_DEBUG=1 flask run
