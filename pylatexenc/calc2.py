import re
import ast
import math
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from tex_to_python import tex_to_python #Función con equivalencias de símbolos de LaTex a Python 
from parse_blocks import parse_eq_block, parse_alg_block


# -------------------------------------------------------------------
# Leer archivo
# -------------------------------------------------------------------
with open("C:/Users/anera/OneDrive/Documentos/USC/4º/TFG/python-latex/python-latex/pylatexenc/calculo3.tex", encoding="utf-8") as f:
    tex = f.read()

# -------------------------------------------------------------------
# Extraer ecuaciones etiquetadas
# -------------------------------------------------------------------

namespace = {"math": math, "__latex_alias__": {}}  # Los alias los guardaremos en oculto para que no se confundan con el resto de variables


def find_algorithmic_and_equation_nodes(nodes):
    """Toma una lista de nodos y devuelve una lista con los nodos que son del tipo algorithmic"""
    env_nodes = []
    
    def search_recursive(node_list):
        for node in node_list:
            # Si es un entorno equation o algorithmic, lo añadimos
            if isinstance(node, LatexEnvironmentNode) and node.envname in ("equation", "algorithmic"):
                env_nodes.append(node)
            # Si el nodo tiene subnodos, buscar recursivamente
            if hasattr(node, 'nodelist') and node.nodelist: # Tiene atributo nodelist y no está vacío
                search_recursive(node.nodelist)
            # Para nodos macro con argumentos que puedan contener subnodos
            elif hasattr(node, 'nodeargd') and node.nodeargd: 
                for arg in node.nodeargd.argnlist:
                    if arg and hasattr(arg, 'nodelist') and arg.nodelist:
                        search_recursive(arg.nodelist)
    
    search_recursive(nodes)
    return env_nodes

    

       
    # Procesar el contenido del entorno algorithmic
    #for subnode in node.nodelist:
    #    print(f"  - {type(subnode).__name__}: {subnode}")



def parse_algorithmic(nodelist):  # AÑADIR LA FUNCIÓN DE RECORRER Y APLICAR LA FUNCIÓN CORRESP SEGUN SEA ALG O EQ
    """
    Wrapper que parsea todo el nodelist de un environment algorithmic.
    Devuelve la lista de sentencias (estructura anidada).
    """
    stmts, _ = parse_alg_block(nodelist, 0, end_tokens=None)
    return stmts


# -------------------------------------------------------------------
# Ejecutar el árbol del algoritmo
# -------------------------------------------------------------------

def ejecutar(algo, ns):
    for step in algo:
        if step["type"] == "assign":
            exec(step["code"], ns)
            # print("Ejecutando:", step["code"])
        elif step["type"] == "if":
            if eval(step["cond"], ns):
                ejecutar(step["body"], ns)
            else:
                ejecutar(step["else"], ns)
        elif step["type"] == "while":
            while eval(step["cond"], ns):
                ejecutar(step["body"], ns)
        elif step["type"] == "return":
            return ns[step["expr"]]
    return None

# -------------------------------------------------------------------
# Extraer entornos con latexwalker
# -------------------------------------------------------------------
walker = LatexWalker(tex)
nodes, _, _ = walker.get_latex_nodes()


env_nodes = find_algorithmic_and_equation_nodes(nodes)
for node in env_nodes:
    if node.envname == "algorithmic":
        print(f"\nEncontrado entorno algorithmic en posición {node.pos}")
        # Convertir el entorno algorithmic a una estructura jerárquica
        algorithm, _ = parse_alg_block(node)
        print("Ejecutando algoritmo:")
        from pprint import pprint
        pprint(algorithm)
        print("\n")
        res = ejecutar(algorithm, namespace)
        print(f"\nResultado del algoritmo: {res:.6f}")
    if node.envname == "equation":
        print(f"\nEncontrado entorno equation en posición {node.pos}")
        var_dict = parse_eq_block(node)
        code = var_dict["alias"] + "=" + var_dict["value"]
        print("Ejecutando:", code)
        exec(code,namespace)  # Almacenar variables y funciones en namespace
        namespace["__latex_alias__"][var_dict["name"]] = var_dict["alias"]  # Almacenar el nombre para que se corresponda con el alias


#print(f"\nRaíz aproximada: {res:.6f}")
#{exec("valor=f(c)",namespace)}
#print(f"Valor de f en la raíz encontrada: {namespace["valor"]:.6f}")
