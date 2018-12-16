#!/usr/local/bin/python3
import sys
import argparse
import json
from pandasworker import PandasWorker

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("worker_type")
    args = parser.parse_args()

    # Cargamos el json de la entrada estándar.
    ejercicios = json.loads(sys.stdin.read())

    if args.worker_type == "pandas":
        worker = PandasWorker(ejercicios)

    worker.correr()
    print(json.dumps(worker.respuestas()))
