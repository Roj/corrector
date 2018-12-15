from abc import ABC, abstractmethod
import ast

class Worker(ABC):
    def __init__(self, ejercicios):
        self.ejercicios = ejercicios

    @staticmethod
    def codigo_es_seguro(codigo):
        """
        Función que asegura que el código sea más o menos seguro de ejecutar.
        Revisa que no haya imports, o llamadas extrañas.
        """
        metodos_prohibidos = ["breakpoint", "classmethod", "compile", "dir",
            "compile", "eval", "exec", "locals", "memoryview", "object", "open",
            "super", "__import__"]
        root = ast.parse(codigo)
        for nodo in ast.walk(root):
            if isinstance(nodo, ast.Import) or isinstance(nodo, ast.ImportFrom):
                return False
            if isinstance(nodo, ast.Name):
                if nodo.id in metodos_prohibidos:
                    return False
        return True

    @abstractmethod
    def correr(self):
        return

    @abstractmethod
    def respuestas(self):
        return
