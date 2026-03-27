from .converter import tex_to_python_with_alias

# Función para extraer recursivamente el texto de un nodelist
def extract_text_from_node(node, cond = False): 
    """Extrae todo el texto de un nodo y sus subnodos recursivamente
        Si cond = True, entonces se interpreta como una condición y se reemplaza = por == """
    # Texto plano
    if hasattr(node, 'chars'):
        return node.chars
    # Macro (\ln, \alpha, \sqrt, etc)
    if hasattr(node,'macroname'):
        str = "\\" + node.macroname
        # Si tiene argumentos, añadirlos
        if hasattr(node, 'nodeargd') and node.nodeargd:
            for arg in node.nodeargd.argnlist:
                if arg is None:
                    continue
                delimiters = getattr(arg, 'delimiters', None)
                if delimiters and delimiters[0] == '[':
                    str += "[" + extract_text_from_node(arg) + "]"
                elif delimiters and delimiters[0] == '(':
                # Llamada a función: reconstruir con paréntesis sin backslash
                    str = node.macroname + "(" + extract_text_from_node(arg) + ")"
                else:
                    str += "{" + extract_text_from_node(arg) + "}"
                
        return str
    # Nodos con subnodos
    if hasattr(node, 'nodelist'):
        text_parts = []
        for subnode in node.nodelist:
            text_parts.append(extract_text_from_node(subnode))
        str = ''.join(text_parts)
        delimiters = getattr(node, 'delimiters', None)
        if delimiters and delimiters[0] == '(':
            str = "(" + result + ")"
        if cond:
            str = str.replace("=", "==")
        return str
    if hasattr(node, 'argnlist'):
        text_parts = []
        for subnode in node.argnlist:
            text_parts.append(extract_text_from_node(subnode)) 
        return ''.join(text_parts)
    #elif hasattr(node, 'latex_verbatim'):
        # Para nodos que tienen método latex_verbatim
    #    return node.latex_verbatim()
    else:
        return ""
        
# -------------------------------------------------------------------
# PARSEAR ENTORNO EQUATION
# -------------------------------------------------------------------

def parse_eq_block(env_node,namespace):

    """
    Procesa un entorno equation y devuelve un diccionario:
    
    {
        "name": nombre interno python,
        "alias": forma latex del lado izquierdo,
        "type": calc o res según sea cálculo o resultado,
        "value": valor python evaluado o lambda
    }
    """

    def node_to_latex(env_node):
        """
        Reconstruye el texto original en LaTeX a partir de un nodo.
        """
        str = ""
        for n in env_node.nodelist:
            if hasattr(n, "macroname") and n.macroname == "label":
                return str     
            str += extract_text_from_node(n)

    def extract_label(env_node):
        """
        Extrae el texto dentro de r"\label{...}"
        """
        for n in env_node.nodelist:
            if hasattr(n, "macroname") and n.macroname == "label":
                label = extract_text_from_node(n.nodeargd)
                return label
        return None
    
    def extract_left_right(env_node):
        """
        Recupera la ecuación completa y la separa en lado izquierdo (left) y derecho (right).
        """
        full = node_to_latex(env_node)

        if "=" not in full:
            raise ValueError("Equation environment without '='")

        left, right = full.split("=", 1)
        return left.strip(), right.strip()
    
    # 1. Extraer label
    label = extract_label(env_node)

    # 2. Extraer left y right
    left, right = extract_left_right(env_node)

    name = left  # lo que el usuario escribió realmente

    # =============================================
    #  FUNCIÓN (forma f(x), g(a,b), etc.)
    # =============================================
    if "(" in left and left.endswith(")"):  
        # nombre interno = el label si existe, si no, lo que está a la izquierda del "("
        alias = label.split(":")[2]  if label else left.split("(", 1)[0]

        #si es cálculo o resultado
        type = label.split(":")[1]  if label else "calc"

        # extraer parámetros
        args = left[left.index("(") + 1 : -1].split(",")   # lista desde el primer parámetro hasta el último antes de ")"
        args = [a.strip() for a in args if a.strip()]   # quitar espacios si hay
        right = tex_to_python_with_alias(right,namespace)  # Traducir a Python

        # construir lambda dinámicamente
        func = f"lambda {', '.join(args)}: {right}"

        return {
            #"type": "function",
            "name": name,
            "alias": alias,
            "type": type,
            "value": func,
        }

    # =============================================
    # VARIABLE
    # =============================================

    #Extraer label
    alias = label.split(":")[2] if label else left  # si no hay label, usamos left literal
    #si es cálculo o resultado
    type = label.split(":")[1]  if label else "calc"

    value = tex_to_python_with_alias(right,namespace)

    # intentar evaluar numéricamente
    # try:
    #    value = eval(right, {"math": math})
    # except Exception:
        # si no se puede evaluar, lo guardamos como string python
    #    value = right
    return {
        #"type": "variable",
        "name": name,
        "alias": alias,
        "type": type,
        "value": value,
    }


# -------------------------------------------------------------------
# PARSEAR ENTORNO ALGORITHMIC (convertirlo en una estructura jerárquica)
# -------------------------------------------------------------------

def parse_alg_block(alg_node, namespace, start=0, end_tokens=None):
    """
    Parsea nodos desde start hasta encontrar un nodo macro cuyo macroname (upper)
    esté en end_tokens. end_tokens puede ser None o lista de strings (ej: ["ENDIF"]).
    Devuelve (stmts, idx) donde idx es el índice del nodo que terminó el bloque
    (el END token encontrado) o len(nodelist) si se llegó al final.
    stmts es una lista de instrucciones tipo dict.
    """
    if end_tokens is None:
        end_tokens = []

    if hasattr(alg_node,"nodelist"): 
        nodelist = alg_node.nodelist
    else:
        nodelist = alg_node
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
                translated = tex_to_python_with_alias(code_txt, namespace)
                stmts.append({"type": "assign", "code": translated})
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
                stmts.append({"type": "return", "expr": tex_to_python_with_alias(arg.strip(),namespace)})
                continue


            # IF / ELSIF / ELSE 
            elif name == "IF":
                # condición normalmente en siguiente nodo (group o math)
                cond = ""
                if (i + 1) < L:
                    nxt = nodelist[i + 1]
                    if hasattr(nxt, "nodelist") and nxt.nodelist:
                        cond = extract_text_from_node(nxt, cond=True) # cond = true para interpretar = como ==
                        i += 1  # consumimos el argumento

                # recorrer hasta ELSIF/ELSE/ENDIF
                body, idx = parse_alg_block(nodelist, namespace, i + 1, end_tokens=["ELSIF", "ELSE", "ENDIF"])
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
                    body2, cur_idx = parse_alg_block(nodelist, namespace, cur_idx + 1, end_tokens=["ELSIF", "ELSE", "ENDIF"])
                    branches.append(("ELSIF", cond2, body2))
                    token = None
                    if cur_idx < L and hasattr(nodelist[cur_idx], "macroname"):
                        token = nodelist[cur_idx].macroname.upper()

                # ELSE (opcional)
                else_body = []
                if cur_idx < L and hasattr(nodelist[cur_idx], "macroname") and nodelist[cur_idx].macroname.upper() == "ELSE":
                    # recorrer ELSE hasta ENDIF
                    else_body, cur_idx = parse_alg_block(nodelist, namespace, cur_idx + 1, end_tokens=["ENDIF"])

                # cur_idx ahora apunta a ENDIF (or al final)
                # Avanzar i a ese ENDIF (si existe)
                i = cur_idx
                # Construir un nodo IF estructurado: 
                #  - cond: condición del primer IF 
                #  - body: cuerpo del primer IF
                #  - else: si hay ELSIFs, representarlos como IFs anidados dentro de ELSE 
                def branches_to_nested(branches, else_block):
                    # branches: list of ("IF"/"ELSIF", cond, body)
                    first = branches[0]
                    if len(branches) == 1:  # Si no hay ningún ELSIF
                        return {"type": "if", "cond": tex_to_python_with_alias(first[1].strip(),namespace), "body": first[2], "else": else_block}
                    else:
                        # nest: else contains the nested branch structure
                        nested_else = branches_to_nested(branches[1:], else_block)
                        return {"type": "if", "cond": tex_to_python_with_alias(first[1].strip(),namespace), "body": first[2], "else": [nested_else]}


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

                body, idx = parse_alg_block(nodelist, namespace, i + 1, end_tokens=["ENDWHILE"])
                stmts.append({"type": "while", "cond": tex_to_python_with_alias(cond.strip(), namespace), "body": body})
                # Avanzar i a ENDWHILE (si existe)
                if idx < L and hasattr(nodelist[idx], "macroname") and nodelist[idx].macroname.upper() == "ENDWHILE":
                    i = idx + 1
                else:
                    i = idx
                continue

        # si no es macro reconocible, simplemente saltar (o podrías registrar)
        i += 1

    # fin while
    return stmts, i