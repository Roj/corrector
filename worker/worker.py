from abc import ABC, abstractmethod
import ast
import importlib

class Worker(ABC):

    @staticmethod
    def codigo_es_seguro(codigo):
        """
        Función que asegura que el código sea más o menos seguro de ejecutar.
        Revisa que no haya imports, o llamadas extrañas.
        """
        metodos_prohibidos = ["breakpoint", "classmethod", "compile", "dir",
            "compile", "eval", "exec", "locals", "memoryview", "object", "open",
            "super", "__import__"]
        try:
            root = ast.parse(codigo)
        except SyntaxError:
            return False
        for nodo in ast.walk(root):
            if isinstance(nodo, ast.Import) or isinstance(nodo, ast.ImportFrom):
                return False
            if isinstance(nodo, ast.Name):
                if nodo.id in metodos_prohibidos:
                    return False
        return True

    @staticmethod
    def cargar_como_modulo(codigo, modulo = None):
        """Escribe el código a un archivo y lo importa para poder utilizarlo.
        Como funciona de módulo, el namespace es reservado y no puede acceder
        a nuestras variables."""
        with open("ejercicio.py","w") as f:
            f.write(codigo)
        # Si corremos de nuevo __import__, se usa el cache y no se refleja el
        # nuevo código. importlib.reload arregla esto.
        if modulo is not None:
            return importlib.reload(modulo)
        return importlib.__import__("ejercicio")

    @abstractmethod
    def correr_trabajo(self, ejercicios):
        return

