import re

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

    # =================================
    # 1. Operadores relacionales
    # =================================
    replacements = {
        r"\leq": "<=",
        r"\geq": ">=",
        r"\neq": "!=",
        r"\ne": "!=",
        r"\lt": "<",
        r"\gt": ">",
        r"\le": "<=",
        r"\ge": ">=",
        r"\leftarrow": "="
    }

    # Aplicar reemplazos
    for latex, py in replacements.items():
        expr = expr.replace(latex, py)
    

    # =================================
    # 2. Funciones matemáticas
    # =================================
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
    }

    # Aplicar reemplazos
    for latex, py in math_funcs.items():
        expr = expr.replace(latex, py)


    # =================================
    # 3. Operaciones matemáticas
    # =================================
    oper = {
        r"^": "**",
        r"\div": "/",
        r"\times": "*",
        r"\cdot": "*",
    }
    for latex, py in oper.items():
        expr = expr.replace(latex, py)


    # =================================
    # 4. Sustituir {  } por ( )
    # =================================
    expr = expr.replace("{", "(").replace("}", ")")


    # =================================
    # 5. Valores absolutos |x| → abs(x)
    # =================================
    expr = re.sub(r"\|(.*?)\|", r"abs(\1)", expr)


    # =================================
    # 6. Normalizar espacios
    # =================================
    expr = re.sub(r"\s+", " ", expr).strip()


    # =================================
    # 7. Letras griegas  (No están pi, Pi, Sigma)
    # =================================
    griegas = {
        r"\alpha": "alpha",
        r"\beta": "beta",
        r"\gamma": "gamma",
        r"\delta": "delta",
        r"\epsilon": "epsilon",
        r"\zeta": "zeta",
        r"\eta": "eta",
        r"\theta": "theta",
        r"\iota": "iota",
        r"\kappa": "kappa",
        r"\lambda": "lambda",
        r"\mu": "mu",
        r"\nu": "nu",
        r"\xi": "xi",
        r"\rho": "rho",
        r"\sigma": "sigma",
        r"\tau": "tau",
        r"\upsilon": "upsilon",
        r"\phi": "phi",
        r"\chi": "chi",
        r"\psi": "psi",
        r"\omega": "omega",
        # Mayúscula
        r"\Gamma": "Gamma",
        r"\Delta": "Delta",
        r"\Theta": "Theta",
        r"\Lambda": "Lambda",
        r"\Xi": "Xi",
        r"\Phi": "Phi",
        r"\Psi": "Psi",
        r"\Omega": "Omega",
    }
    for latex, py in griegas.items():
        expr = expr.replace(latex, py)

    return expr


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

