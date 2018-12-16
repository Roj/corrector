## Corrector automático

Es un proyecto basado en Flask y Docker que apunta a corregir automáticamente
guías de ejercicios basadas en código. Puntualmente, guías donde sea necesario
programar en PySpark o Pandas. 

`app.py` tiene la aplicación Flask que sirve como front-end del corrector.

`corrector.py` maneja la información de las guías (que se cargan a partir de
los archivos YAML en el directorio `guias/`) y la cola de procesamiento.

Contenedores de Docker funcionarán como Workers que ejecutan una sola guía a
la vez -- se levanta un contenedor, se ejecuta el código recibido y se
devuelve la salida del código.

El código del Worker está en `worker`, con su Dockerfile. `worker.py` es la
clase abstracta con la interfaz para cada tipo de worker (según el tipo de
guiá que se ejecute: Pandas, Spark,...) y funciones auxiliares, y `entry.py`
es el script de entrada del contenedor que trabaja con la entrada y salida
estándar.

Para reducir el riesgo que conlleva ejecutar código arbitrario, se tienen
las siguientes consideraciones:  

- el código recibido se ejecuta en un contenedor de Docker levantado
específicamente para eso,
- se analiza el árbol sintáctico del código para revisar que no haya
llamadas a funciones que pueden servir como vector de ataque, imports o
similares,
- se encapsula el código en una función,
- se carga el código como módulo con un namespace distinto, y
- se corre el código bajo un try/except para evitar problemas de excepciones.
