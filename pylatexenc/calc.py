import re
import ast
import math
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from tex_to_python import tex_to_python #Función con equivalencias de símbolos de LaTex a Python 


# -------------------------------------------------------------------
# Leer archivo
# -------------------------------------------------------------------
with open("C:/Users/anera/OneDrive/Documentos/USC/4º/TFG/python-latex/python-latex/pylatexenc/calculo2.tex", encoding="utf-8") as f:
    tex = f.read()

# -------------------------------------------------------------------
# Extraer ecuaciones etiquetadas
# -------------------------------------------------------------------
eq_pattern = re.compile(
    r"\\begin\{equation\}(.*?)\\label\{eq:calc:(.*?)\}.*?\\end\{equation\}",
    # Encontrar estructuras tipo 
    #   \begin{equation} 
    #       (1) 
    #       \label{eq:calc:(2)} 
    #       (?)
    #   \end{equation}
    re.S    # Incluir también la posibilidad de una nueva línea en (?)
)
equations = {label.strip(): expr.strip() for expr, label in eq_pattern.findall(tex)} # Crea un diccionario con {(2):(1)} para todas las eq del doc

namespace = {"math": math}

for label, expr in equations.items():
    left, right = expr.split("=", 1)
    right = tex_to_python(right.strip())
    code = f"{label} = lambda x: {right}" if "(x)" in left else f"{label} = {right}"
    print("Ejecutando:", code)
    exec(code,namespace)  # Almacenar variables y funciones en namespace



def find_algorithmic_nodes(nodes):
    """Toma una lista de nodos y devuelve una lista con los nodos que son del tipo algorithmic"""
    algorithmic_nodes = []
    
    def search_recursive(node_list):
        for node in node_list:
            # Si es un entorno algorithmic, lo añadimos
            if isinstance(node, LatexEnvironmentNode) and node.envname == "algorithmic":
                algorithmic_nodes.append(node)
            
            # Si el nodo tiene subnodos, buscar recursivamente
            if hasattr(node, 'nodelist') and node.nodelist: # Tiene atributo nodelist y no está vacío
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
def extract_text_from_node(node, cond = False):
    """Extrae todo el texto de un nodo y sus subnodos recursivamente"""
    if hasattr(node, 'chars'):
        return node.chars
    elif hasattr(node, 'nodelist'):
        # Para nodos que contienen otros nodos (grupos, entornos, etc.)
        text_parts = []
        for subnode in node.nodelist:
            text_parts.append(extract_text_from_node(subnode)) 
        str = ''.join(text_parts)
        if cond:
            str = str.replace("=", "==")
        return str
    elif hasattr(node, 'latex_verbatim'):
        # Para nodos que tienen método latex_verbatim
        return node.latex_verbatim()
    else:
        return ""

def parse_block(nodelist, start=0, end_tokens=None):
    """
    Parsea nodos desde start hasta encontrar un nodo macro cuyo macroname (upper)
    esté en end_tokens. end_tokens puede ser None o lista de strings (ej: ["ENDIF"]).
    Devuelve (stmts, idx) donde idx es el índice del nodo que terminó el bloque
    (el END token encontrado) o len(nodelist) si se llegó al final.
    stmts es una lista de instrucciones tipo dict.
    """
    if end_tokens is None:
        end_tokens = []

    stmts = []
    i = start
    L = len(nodelist)

    while i < L:
        node = nodelist[i]

        # si es macro comprobamos si cierra el bloque
        if hasattr(node, "macroname"):
            name = node.macroname.upper()

            # si es un token de cierre para este bloque, devolvemos
            if name in end_tokens:
                return stmts, i

            # STATE: texto después hasta siguiente macro
            if name == "STATE":
                j = i + 1
                code_parts = []
                while j < L:
                    nj = nodelist[j]
                    if hasattr(nj, "macroname"):
                        # si siguiente es macro, paramos
                        break
                    code_parts.append(extract_text_from_node(nj))
                    j += 1
                code_txt = ''.join(code_parts).strip()
                stmts.append({"type": "assign", "code": tex_to_python(code_txt)})
                i = j  # continuar desde j (vamos a hacer el incremento al final)
                continue

            # RETURN: puede tener la expresión en el siguiente nodo
            elif name == "RETURN":
                arg = ""
                # mirar siguiente nodo si existe
                if (i + 1) < L:
                    nxt = nodelist[i + 1]
                    arg = extract_text_from_node(nxt)
                    i += 1  # consumimos el argumento
                stmts.append({"type": "return", "expr": tex_to_python(arg.strip())})
                continue


            # IF / ELSIF / ELSE handling requires special flow
            elif name == "IF":
                # condición normalmente en siguiente nodo (group o math)
                cond = ""
                if (i + 1) < L:
                    nxt = nodelist[i + 1]
                    if hasattr(nxt, "nodelist") and nxt.nodelist:
                        cond = extract_text_from_node(nxt, cond=True) # cond = true para interpretar = como ==
                        i += 1  # consumimos el argumento

                # recorrer hasta ELSIF/ELSE/ENDIF
                body, idx = parse_block(nodelist, i + 1, end_tokens=["ELSIF", "ELSE", "ENDIF"])
                branches = [("IF", cond, body)]

                # manejar todos los ELSIF que haga falta
                token = None
                if idx < L and hasattr(nodelist[idx], "macroname"):
                    token = nodelist[idx].macroname.upper()  # Puede ser ELSIF, ELSE, WHILE, ENDIF

                cur_idx = idx
                while token == "ELSIF":
                    # condición después de ELSIF
                    cond2 = ""
                    if (cur_idx + 1) < L:
                        nxt = nodelist[cur_idx + 1]
                        cond2 = extract_text_from_node(nxt, cond=True) # cond = true para interpretar = como ==
                        cur_idx += 1
                    # recorrer hasta el siguiente ELSIF/ELSE/ENDIF
                    body2, cur_idx = parse_block(nodelist, cur_idx + 1, end_tokens=["ELSIF", "ELSE", "ENDIF"])
                    branches.append(("ELSIF", cond2, body2))
                    token = None
                    if cur_idx < L and hasattr(nodelist[cur_idx], "macroname"):
                        token = nodelist[cur_idx].macroname.upper()

                # ELSE (opcional)
                else_body = []
                if cur_idx < L and hasattr(nodelist[cur_idx], "macroname") and nodelist[cur_idx].macroname.upper() == "ELSE":
                    # recorrer ELSE hasta ENDIF
                    else_body, cur_idx = parse_block(nodelist, cur_idx + 1, end_tokens=["ENDIF"])

                # cur_idx should now point to ENDIF (or EOF)
                # Advance i to that ENDIF (if present)
                i = cur_idx
                # Build a structured if node: keep branches and else
                # For backward compatibility with earlier code, produce "cond","body","else"
                # We'll compose a single IF where:
                #  - cond: first IF cond
                #  - body: first IF body
                #  - else: if ELSIFs exist, represent them as nested ifs in 'else' chain
                # Convert branches (IF + ELSIF*) into nested structure:
                def branches_to_nested(branches, else_block):
                    # branches: list of ("IF"/"ELSIF", cond, body)
                    first = branches[0]
                    if len(branches) == 1:  # Si no hay ningún ELSIF
                        return {"type": "if", "cond": tex_to_python(first[1].strip()), "body": first[2], "else": else_block}
                    else:
                        # nest: else contains the nested branch structure
                        nested_else = branches_to_nested(branches[1:], else_block)
                        return {"type": "if", "cond": tex_to_python(first[1].strip()), "body": first[2], "else": [nested_else]}


                if_node = branches_to_nested(branches, else_body)
                stmts.append(if_node)

                if i < L and hasattr(nodelist[i], "macroname") and nodelist[i].macroname.upper() == "ENDIF":
                    i += 1 # consumimos el \ENDIF
                continue

            # WHILE
            elif name == "WHILE":
                cond = ""
                if (i + 1) < L:
                    nxt = nodelist[i + 1]
                    if hasattr(nxt, "nodelist") and nxt.nodelist:
                        cond = extract_text_from_node(nxt, cond=True)
                        i += 1  # consumimos el argumento

                body, idx = parse_block(nodelist, i + 1, end_tokens=["ENDWHILE"])
                stmts.append({"type": "while", "cond": tex_to_python(cond.strip()), "body": body})
                # advance i to after ENDWHILE if present
                if idx < L and hasattr(nodelist[idx], "macroname") and nodelist[idx].macroname.upper() == "ENDWHILE":
                    i = idx + 1
                else:
                    i = idx
                continue

        # si no es macro reconocible, simplemente saltar (o podrías registrar)
        i += 1

    # fin while
    return stmts, i

def parse_algorithmic(nodelist):
    """
    Wrapper que parsea todo el nodelist de un environment algorithmic.
    Devuelve la lista de sentencias (estructura anidada).
    """
    stmts, _ = parse_block(nodelist, 0, end_tokens=None)
    return stmts

# antes no se estaba evaluando en la lista, si no en la clase. Aqui, se hace un repaso de todos los entornos algoritmo y se ponen en una lista
algorithm=list(range(len(algorithmic_nodes)))
for i, algenv in enumerate(algorithmic_nodes):
    algorithm[i] = parse_algorithmic(algenv.nodelist)  

print("\nEstructura del algoritmo:")
from pprint import pprint
pprint(algorithm)

# -------------------------------------------------------------------
# Ejecutar el árbol del algoritmo
# -------------------------------------------------------------------

def ejecutar(algo, ns):
    for step in algo:
        if step["type"] == "assign":
            exec(step["code"], ns)
            #print("Ejecutando:", step["code"])
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



root = ejecutar(algorithm[0], namespace)

print(f"\nRaíz aproximada: {root:.6f}")
#{exec("valor=f(c)",namespace)}
#print(f"Valor de f en la raíz encontrada: {namespace["valor"]:.6f}")
