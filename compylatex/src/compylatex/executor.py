import re
import math
from .parser import parse_env_node
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode


def compylatex(fichero_latex, output=None):
    with open(fichero_latex, encoding="utf-8") as f:
        tex = f.read()
    # tex_resultado es una copia que iremos modificando con los resultados
    tex_resultado = tex
    # -------------------------------------------------------------------
    # EXTRAER ECUACIONES ETIQUETADAS
    # -------------------------------------------------------------------
    namespace = {"math": math, "__latex_alias__": {}}  # Los alias los guardaremos en oculto para que no se confundan con el resto de variables

    # -------------------------------------------------------------------
    # EXTRAER ENTORNOS CON LATEXWALKER
    # -------------------------------------------------------------------
    walker = LatexWalker(tex)
    from pprint import pprint
    nodes, _, _ = walker.get_latex_nodes()
    
    substitutions = []  # lista de (pos, len, nuevo_texto). La guardamos para luego aplicar las sustituciones todas juntas y controlar las posiciones en el nuevo documento
    env_nodes = find_algorithmic_and_equation_nodes(nodes)
    for node in env_nodes:
        # print(node.envname)
        result = parse_env_node(node,namespace)
        if result is None:
            continue

        if node.envname == "algorithm": # Convertir el entorno algorithmic a una estructura jerárquica
            # print(f"\nEncontrado entorno algorithmic en posición {node.pos}")
            # pprint(result["stmts"])
            name, res = ejecutar(result["stmts"], namespace)
            print(f"Resultado del algoritmo: {name} = {res:.6f}")
        if node.envname == "equation":
            # print(f"\nEncontrado entorno equation en posición {node.pos}")
            if result["type"] == "res":
                # Es un resultado: insertar el valor actual del namespace en tex_resultado
                alias = result["alias"]
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
                    print(f"Advertencia: '{alias}' no encontrado en namespace")
            else:
                # Es un cálculo o definición: ejecutar normalmente
                code = result["alias"] + "=" + result["value"]
                print("Ejecutando:", code)
                exec(code, namespace)

    # -------------------------------------------------------------------
    # SUSTIRUIR RESULTADOS 
    # -------------------------------------------------------------------
    tex_resultado = tex
    for pos, length, new_text in sorted(substitutions, key=lambda x: x[0], reverse=True): # De atrás a delante para que las posiciones no cambie respecto al original
        tex_resultado = tex_resultado[:pos] + new_text + tex_resultado[pos + length:]
    
    # -------------------------------------------------------------------
    # ESCRIBIR ARCHIVO RESULTADO
    # -------------------------------------------------------------------
    if output is None:
        output = fichero_latex  # sobreescribe el original
    with open(output, "w", encoding="utf-8") as f:
        f.write(tex_resultado)
    print(f"\nResultado guardado en {output}")




# Función para identificar los nodos del tipo algorithmic o equation
def find_algorithmic_and_equation_nodes(nodes):
    """Toma una lista de nodos y devuelve una lista con los nodos que son del tipo algorithmic o equation"""
    env_nodes = []
    
    def search_recursive(node_list):
        for node in node_list:
            # Si es un entorno equation o algorithmic, lo añadimos
            if isinstance(node, LatexEnvironmentNode) and node.envname in ("equation", "algorithm"):
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


# -------------------------------------------------------------------
# Ejecutar el árbol del algoritmo
# -------------------------------------------------------------------

def ejecutar(algo, ns):
    for step in algo:
        if step["type"] == "assign":
            exec(step["code"], ns)
        elif step["type"] == "if":
            if eval(step["cond"], ns):
                result = ejecutar(step["body"], ns)
            else:
                result = ejecutar(step["else"], ns)
            if result is not None: 
                return result
        elif step["type"] == "while":
            while eval(step["cond"], ns):
                result = ejecutar(step["body"], ns)
                if result is not None:
                    return result
        elif step["type"] == "repeat":
            while True:
                result = ejecutar(step["body"], ns)
                if result is not None:
                    return result
                if eval(step["cond"], ns):
                    break
        elif step["type"] == "return":
            return step["expr"], ns[step["expr"]]
        elif step["type"] == "print":
            exec(f"print({step['expr']})", ns)
    return None

