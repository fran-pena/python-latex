import re
import math
from .parser import parse_eq_block, parse_alg_block
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode


def compylatex(fichero_latex, output=None):
    with open(fichero_latex, encoding="utf-8") as f:
        tex = f.read()
# -------------------------------------------------------------------
# Leer archivo
# -------------------------------------------------------------------
## with open("C:/Users/anera/OneDrive/Documentos/USC/4º/TFG/python-latex/pylatexenc/calculo.tex", encoding="utf-8") as f:
##    tex = f.read()

# tex_resultado es una copia que iremos modificando con los resultados
    tex_resultado = tex
# -------------------------------------------------------------------
# Extraer ecuaciones etiquetadas
# -------------------------------------------------------------------

    namespace = {"math": math, "__latex_alias__": {}}  # Los alias los guardaremos en oculto para que no se confundan con el resto de variables

# -------------------------------------------------------------------
# Reinsertar resultado en tex_resultado
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# Extraer entornos con latexwalker
# -------------------------------------------------------------------
    walker = LatexWalker(tex)
    nodes, _, _ = walker.get_latex_nodes()
    
    substitutions = []  # lista de (pos, len, nuevo_texto). La guardamos para luego aplicar las sustituciones todas juntas y controlar las     posiciones en el nuevo documento
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
                    value_str = f"{value:.6f}" if isinstance(value, float) else str(value)
                    env_text = tex[node.pos : node.pos + node.len]
                    new_env = re.sub(
                        r'(=\s*)(\\label\{eq:res:' + re.escape(alias) + r'\})',
                        r'\g<1>' + value_str + r'\n    \2',
                        env_text,
                        flags=re.DOTALL
                    )
                    substitutions.append((node.pos, node.len, new_env))
                else:
                    print(f"Advertencia: '{alias}' no encontrado en namespace, no se inserta resultado")
            else:
                # Es un cálculo o definición: ejecutar normalmente
                code = var_dict["alias"] + "=" + var_dict["value"]
                print("Ejecutando:", code)
                name_key = var_dict["name"].split('(')[0].strip()
                namespace["__latex_alias__"][name_key] = var_dict["alias"]  # Almacenar el nombre para que se corresponda con el alias
                exec(code, namespace)  # Almacenar variables y funciones en namespace
            
    # --------------------------------------------------------------------
    # Sustituir resultados 
    # -------------------------------------------------------------------
    # Aplicar sustituciones de atrás hacia adelante
    tex_resultado = tex
    for pos, length, new_text in sorted(substitutions, key=lambda x: x[0], reverse=True): # De atrás a delante para que las posiciones no cambie respecto al OG
        tex_resultado = tex_resultado[:pos] + new_text + tex_resultado[pos + length:]
    
    # -------------------------------------------------------------------
    # Escribir archivo resultado
    # -------------------------------------------------------------------
    #output_path = "C:/Users/anera/OneDrive/Documentos/USC/4º/TFG/python-latex/pylatexenc/calculo_resultado.tex"
    #with open(output_path, "w", encoding="utf-8") as f:
    #    f.write(tex_resultado)
    #print(f"\nResultado guardado en {output_path}")
    if output is None:
        output = fichero_latex  # sobreescribe el original
    with open(output, "w", encoding="utf-8") as f:
        f.write(tex_resultado)
    print(f"\nResultado guardado en {output}")

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

