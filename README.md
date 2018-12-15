## Corrector automático

Es un proyecto basado en Flask y Docker que apunta a corregir automáticamente
guías de ejercicios basadas en código. Puntualmente, guías donde sea necesario
programar en PySpark o Pandas. 

`app.py` tiene la aplicación Flask que sirve como front-end del corrector.

`corrector.py` maneja la información de las guías (que se cargan a partir de
los archivos YAML en el directorio `guias/`) y la cola de procesamiento.

Contenedores de Docker funcionarán como Workers que ejecutarán los trabajos
en la cola de procesamiento, y devolverán un estado según la comparación
de la salida esperada y la obtenida.
