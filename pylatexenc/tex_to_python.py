import math
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

