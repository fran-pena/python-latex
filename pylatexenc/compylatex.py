import re
import ast
import math
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
#from tex_to_python import tex_to_python_with_alias #Función con equivalencias de símbolos de LaTex a Python 
from parse_blocks import parse_eq_block, parse_alg_block


# -------------------------------------------------------------------
# Leer archivo
# -------------------------------------------------------------------
with open("C:/Users/anera/OneDrive/Documentos/USC/4º/TFG/python-latex/pylatexenc/calculo.tex", encoding="utf-8") as f:
    tex = f.read()

# tex_resultado es una copia que iremos modificando con los resultados
tex_resultado = tex
# -------------------------------------------------------------------
# Extraer ecuaciones etiquetadas
# -------------------------------------------------------------------

namespace = {"math": math, "__latex_alias__": {}}  # Los alias los guardaremos en oculto para que no se confundan con el resto de variables


def find_algorithmic_and_equation_nodes(nodes):
    """Toma una lista de nodos y devuelve una lista con los nodos que son del tipo algorithmic o equation"""
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

    

def parse_algorithmic(nodelist):  # AÑADIR LA FUNCIÓN DE RECORRER Y APLICAR LA FUNCIÓN CORRESP SEGUN SEA ALG O EQ
    """
    Wrapper que parsea todo el nodelist de un environment algorithmic.
    Devuelve la lista de sentencias (estructura anidada).
    """
    stmts, _ = parse_alg_block(nodelist, namespace, 0, end_tokens=None)
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
            return step["expr"], ns[step["expr"]]
    return None

# -------------------------------------------------------------------
# Reinsertar resultado en tex_resultado
# -------------------------------------------------------------------

def reinsert_result(tex, alias, value):
    value_str = f"{value:.6f}" if isinstance(value, float) else str(value)
    
    # Primero encontrar el entorno equation que contiene el label correcto
    # Luego sustituir solo el RHS dentro de ese entorno
    def replace_match(m):
        env = m.group(0)
        # Dentro del entorno, sustituir lo que hay entre = y \label
        env = re.sub(
            r'(=\s*).*?(\\label\{eq:res:' + re.escape(alias) + r'\})',
            r'\g<1>' + value_str + r'\n    \2',
            env,
            flags=re.DOTALL
        )
        return env
    
    # Primero aislar el entorno correcto (el que contiene ese label específico)
    pattern = re.compile(
        r'\\begin\{equation\}[^}]*?\\label\{eq:res:' + re.escape(alias) + r'\}.*?\\end\{equation\}',
        re.DOTALL
    )
    return pattern.sub(replace_match, tex)


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
        algorithm, _ = parse_alg_block(node, namespace)
        print("Ejecutando algoritmo:")
        from pprint import pprint
        pprint(algorithm)
        name,res = ejecutar(algorithm, namespace)
        print(f"\nResultado del algoritmo: {name} = {res:.6f}")
    if node.envname == "equation":
        print(f"\nEncontrado entorno equation en posición {node.pos}")
        var_dict = parse_eq_block(node,namespace)

        if var_dict["type"] == "res":
            # Es un resultado: insertar el valor actual del namespace en tex_resultado
            alias = var_dict["alias"]
            if alias in namespace:
                value = namespace[alias]
                tex_resultado = reinsert_result(tex_resultado, alias, value)
                print(f"Resultado insertado: {alias} = {value:.6f}" if isinstance(value, float) else f"Resultado insertado: {alias} = {value}")
            else:
                print(f"Advertencia: '{alias}' no encontrado en namespace, no se inserta resultado")
        else:
            # Es un cálculo o definición: ejecutar normalmente
            code = var_dict["alias"] + "=" + var_dict["value"]
            print("Ejecutando:", code)
            namespace["__latex_alias__"][var_dict["name"]] = var_dict["alias"]  # Almacenar el nombre para que se corresponda con el alias
            exec(code, namespace)  # Almacenar variables y funciones en namespace
        

# -------------------------------------------------------------------
# Escribir archivo resultado
# -------------------------------------------------------------------
output_path = "C:/Users/anera/OneDrive/Documentos/USC/4º/TFG/python-latex/pylatexenc/calculo_resultado.tex"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(tex_resultado)
print(f"\nResultado guardado en {output_path}")