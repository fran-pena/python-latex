import re
import math
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode

# -------------------------------------------------------------------
# Leer archivo
# -------------------------------------------------------------------
with open("calculo.tex", encoding="utf-8") as f:
    tex = f.read()

# -------------------------------------------------------------------
# Extraer ecuaciones etiquetadas
# -------------------------------------------------------------------
eq_pattern = re.compile(
    r"\\begin\{equation\}(.*?)\\label\{eq:calc:(.*?)\}.*?\\end\{equation\}",
    re.S
)
equations = {label.strip(): expr.strip() for expr, label in eq_pattern.findall(tex)}

namespace = {"math": math}

def tex_to_python(expr):
    expr = expr.replace(r"\sqrt", "math.sqrt")
    expr = expr.replace("^", "**")
    expr = expr.replace("{", "(").replace("}", ")")
    return expr

for label, expr in equations.items():
    left, right = expr.split("=", 1)
    right = tex_to_python(right.strip())
    code = f"{label} = lambda x: {right}" if "(x)" in left else f"{label} = {right}"
    print("Ejecutando:", code)
    exec(code, namespace)

def find_algorithmic_nodes(nodes):
    algorithmic_nodes = []
    
    def search_recursive(node_list):
        for node in node_list:
            # Si es un entorno algorithmic, lo añadimos
            if isinstance(node, LatexEnvironmentNode) and node.envname == "algorithmic":
                algorithmic_nodes.append(node)
            
            # Si el nodo tiene subnodos, buscar recursivamente
            if hasattr(node, 'nodelist') and node.nodelist:
                search_recursive(node.nodelist)
            # Para nodos macro con argumentos que puedan contener subnodos
            elif hasattr(node, 'nodeargd') and node.nodeargd:
                for arg in node.nodeargd.argnlist:
                    if arg and hasattr(arg, 'nodelist') and arg.nodelist:
                        search_recursive(arg.nodelist)
    
    search_recursive(nodes)
    return algorithmic_nodes

        
# -------------------------------------------------------------------
# Extraer entorno algorithmic con latexwalker
# -------------------------------------------------------------------
walker = LatexWalker(tex)
nodes, _, _ = walker.get_latex_nodes()
algorithmic_nodes = find_algorithmic_nodes(nodes)
for node in algorithmic_nodes:
    print(f"Encontrado entorno algorithmic en posición {node.pos}")
    # Procesar el contenido del entorno algorithmic
    for subnode in node.nodelist:
        print(f"  - {type(subnode).__name__}: {subnode}")

# -------------------------------------------------------------------
# Convertir el entorno algorithmic a una estructura jerárquica
# -------------------------------------------------------------------
def extract_text_from_node(node):
    """Extrae todo el texto de un nodo y sus subnodos recursivamente"""
    if hasattr(node, 'chars'):
        return node.chars
    elif hasattr(node, 'nodelist'):
        # Para nodos que contienen otros nodos (grupos, entornos, etc.)
        text_parts = []
        for subnode in node.nodelist:
            text_parts.append(extract_text_from_node(subnode))
        return ''.join(text_parts)
    elif hasattr(node, 'latex_verbatim'):
        # Para nodos que tienen método latex_verbatim
        return node.latex_verbatim()
    else:
        return ""

def parse_algorithmic(nodelist):
    algo = []
    i = 0
    while i < len(nodelist):
        node = nodelist[i]
        if hasattr(node, "macroname"):
            cmd = node.macroname.upper()
            
            if cmd == "STATE":
                # Buscar el código en los nodos siguientes (hasta el próximo comando)
                code_content = ""
                j = i + 1
                while j < len(nodelist):
                    next_node = nodelist[j]
                    # Si encontramos otro comando algorítmico, terminamos
                    if hasattr(next_node, "macroname") and next_node.macroname in ["STATE", "IF", "WHILE", "ELSE", "ENDIF", "ENDWHILE", "RETURN"]:
                        break
                    # Acumular texto de este nodo
                    code_content += extract_text_from_node(next_node)
                    j += 1
                
                algo.append({"type": "assign", "code": code_content.strip()})
                i = j - 1  # Ajustar el índice para continuar después del código
                
            elif cmd in ["IF", "WHILE"]:
                # Para IF y WHILE, la condición está en los argumentos
                arg = ""
                if node.nodeargd and node.nodeargd.argnlist:
                    # Tomar el primer argumento (la condición)
                    arg_node = node.nodeargd.argnlist[0]
                    if arg_node is not None:
                        arg = extract_text_from_node(arg_node).strip("{}")
                
                if cmd == "IF":
                    body, i = collect_block(nodelist, i+1, "ENDIF", ["ELSE"])
                    else_body = []
                    if body["endcmd"] == "ELSE":
                        else_body, i = collect_block(nodelist, i, "ENDIF")
                    algo.append({"type": "if", "cond": arg, "body": body["content"], "else": else_body})
                else:  # WHILE
                    body, i = collect_block(nodelist, i+1, "ENDWHILE")
                    algo.append({"type": "while", "cond": arg, "body": body["content"]})
                    
            elif cmd == "RETURN":
                # RETURN puede tener argumento opcional
                arg = ""
                if node.nodeargd and node.nodeargd.argnlist:
                    arg_node = node.nodeargd.argnlist[0]
                    if arg_node is not None:
                        arg = extract_text_from_node(arg_node).strip("{}")
                algo.append({"type": "return", "expr": arg})
                
        i += 1
    return algo

def collect_block(nodelist, start, endcmd, extra_end=None):
    """Extrae los nodos hasta encontrar el comando \ENDxxx o uno alternativo"""
    if extra_end is None:
        extra_end = []
    block = []
    i = start
    while i < len(nodelist):
        node = nodelist[i]
        if hasattr(node, "macroname"):
            name = node.macroname.upper()
            if name == endcmd:
                return {"content": parse_algorithmic(block), "endcmd": endcmd}, i
            elif name in extra_end:
                return {"content": parse_algorithmic(block), "endcmd": name}, i
        block.append(node)
        i += 1
    return {"content": parse_algorithmic(block), "endcmd": endcmd}, i

algorithm = parse_algorithmic(algorithmic_nodes)

print("\nEstructura del algoritmo:")
from pprint import pprint
pprint(algorithm)

# -------------------------------------------------------------------
# Ejecutar el árbol del algoritmo
# -------------------------------------------------------------------
def ejecutar(algo, ns):
    result = None
    for step in algo:
        if step["type"] == "assign":
            exec(step["code"], ns)
        elif step["type"] == "if":
            if eval(step["cond"], ns):
                result = ejecutar(step["body"], ns)
            else:
                result = ejecutar(step["else"], ns)
        elif step["type"] == "while":
            while eval(step["cond"], ns):
                result = ejecutar(step["body"], ns)
        elif step["type"] == "return":
            result = eval(step["expr"], ns)
            break
    return result

root = ejecutar(algorithm, namespace)
print(f"\nRaíz aproximada: {root:.6f}")
