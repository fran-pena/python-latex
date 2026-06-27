import re

# -------------------------------------------------------------------
# REEMPLAZAR ALIAS
# -------------------------------------------------------------------
def replace_aliases(expr, namespace):
    """
    Reemplaza names latex por alias internos definidos en namespace["__latex_alias__"].
    """
    if "__latex_alias__" not in namespace:
        return expr

    names = namespace["__latex_alias__"]

    # Ordenar alias del más largo al más corto para evitar colisiones
    sorted_names = sorted(names.keys(), key=len, reverse=True)

    for name in sorted_names:
        alias = names[name]   # alias que se le da en el namespace
        expr = expr.replace(name, alias)

    return expr


# -------------------------------------------------------------------
# TRADUCIR EXPRESIONES LATEX
# -------------------------------------------------------------------
def tex_to_python(expr):
    """
    Convierte expresiones matemáticas en estilo LaTeX a expresiones válidas en Python,
    pero SOLO símbolos que realmente pueden aparecer en entornos 'algorithmic'.
    """

    if expr is None:
        return ""

    # Primero, eliminar espacios redundantes
    expr = expr.strip()

    #Eliminar para que no de problemas 
    expr = expr.replace(r"\left", "").replace(r"\right", "")

    # -------------------------------------------------------------------
    # 1. Operadores relacionales
    # -------------------------------------------------------------------
    replacements = {
        r"\leq": "<=",
        r"\geq": ">=",
        r"\neq": "!=",
        r"\ne": "!=",
        r"\lt": "<",
        r"\gt": ">",
        r"\gets": "=",
        r"\ge": ">=",
        r"\leftarrow": "=",
        r"\le": "<="
    }

    # Aplicar reemplazos
    for latex, py in replacements.items():
        expr = expr.replace(latex, py)
    

    # -------------------------------------------------------------------
    # 2. Funciones matemáticas
    # -------------------------------------------------------------------
    # \sqrt[n]{x} → (x)**(1/n)
    expr = re.sub(
    r'\\sqrt\[([^\]]+)\]\{(.+?)\}',
    r'(\2)**(1/\1)',
    expr
    )
    math_funcs = {
        r"\sqrt": "math.sqrt",
        r"\sin": "math.sin",
        r"\cos": "math.cos",
        r"\tan": "math.tan",
        r"\log": "math.log",
        r"\ln": "math.log",
        r"\exp": "math.exp",
        r"\pi": "math.pi"
    }

    # Aplicar reemplazos
    for latex, py in math_funcs.items():
        expr = expr.replace(latex, py)


    # -------------------------------------------------------------------
    # 3. Operaciones matemáticas
    # -------------------------------------------------------------------
    oper = {
        r"^": "**",
        r"\div": "/",
        r"\times": "*",
        r"\cdot": "*",
    }
    for latex, py in oper.items():
        expr = expr.replace(latex, py)

    # -------------------------------------------------------------------
    # 4. Valores absolutos |x| → abs(x)
    # -------------------------------------------------------------------
    expr = re.sub(r"\|(.*?)\|", r"abs(\1)", expr)

    # -------------------------------------------------------------------
    # 5. Sustituir {  } por ( )
    # -------------------------------------------------------------------
    expr = expr.replace("{", "(").replace("}", ")")

    # -------------------------------------------------------------------
    # 6. Sustituir conectores de algorithmic
    # -------------------------------------------------------------------
    expr = re.sub(r'\\AND', ' and ', expr)
    expr = re.sub(r'\\OR', ' or ', expr)
    expr = re.sub(r'\\NOT', ' not ', expr)
    expr = re.sub(r'\\XOR', ' ^ ', expr)


    # -------------------------------------------------------------------
    # 7. Normalizar espacios
    # -------------------------------------------------------------------
    expr = re.sub(r"\s+", " ", expr).strip()


    return expr

# Función que sustituye primero los alias y luego traduce las expresiones LaTeX
def tex_to_python_with_alias(expr, namespace):
    """
    Reemplaza names latex por alias internos definidos en namespace["__latex_alias__"], 
    y luego convierte expresiones matemáticas en estilo LaTeX a expresiones válidas en Python.
    """
    #print(expr)
    #withalias = replace_aliases(expr,namespace)
    #print(withalias)
    result = replace_aliases(expr, namespace)
    return tex_to_python(result)

