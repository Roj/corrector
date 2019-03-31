build:
	./download_data.py
	docker build -f worker/Dockerfile . -t worker
run:
	docker run -p 127.0.0.1:6000:6000 -d worker
	FLASK_DEBUG=1 flask run --host=0.0.0.0

nodocker_run:
	# Corremos el worker como usuario nobody, cuidando
	# los permisos.
	mkdir -p worker/datos
	cp guias/entradas/* worker/datos/
	chmod 751 . guias guias/salidas
	chmod 640 *.py
	chmod 645 worker/*.py
	chmod 777 worker
	touch worker/ejercicio.py
	chmod 646 worker/ejercicio.py
	cd worker/ && sudo -u nobody PYSPARK_PYTHON=`which python3` python3 entry.py 2>&1 | tee /tmp/worker.log >/dev/null &
	flask run --host 0.0.0.0 2>&1 | tee /tmp/server.log >/dev/null &
test:
	echo abc>pepe.txt
