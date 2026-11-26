#!/usr/bin/env python3
"""
Prueba el parser (extract_text_from_node y compañía) con casos que fallaban o podían fallar.

    python test_parser.py --generar                 # escribe test_parser.tex (para leer o compilar)
    python test_parser.py --generar --para-original # escribe test_parser_original.tex: sin los casos
                                                    # que con el código antiguo dan error y no un valor
    python test_parser.py --verificar               # ejecuta compylatex caso a caso y compara
    python test_parser.py --verificar --paquete compylatex_orig   # lo mismo con otro paquete

Cada caso se ejecuta en su propio documento, así un fallo (o un cuelgue de excepción) en uno no
tapa a los demás. Los valores esperados se calculan aquí con Python puro, sin usar el converter.
Con el paquete original fallan los casos marcados [parser] (extract_text_from_node pierde llaves
o convierte mal el =) y el marcado [alias] (replace_aliases cambia la letra dentro de \\gets).
Los demás pasan también con el original: sirven para comprobar que no se rompió nada.
"""
import contextlib
import importlib
import io
import math
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
TEX = os.path.join(AQUI, "test_parser.tex")

# Variables que usan los casos (se definen al principio del documento)
X, N, A, B = 2, 3, 5, 7
DEFS = [("x", X), ("n", N), ("a", A), ("b", B)]

# -------------------------------------------------------------------------------------------
# Casos de ecuación: (id, qué se prueba, lado derecho en LaTeX, esperado, símbolo del resultado)
# -------------------------------------------------------------------------------------------
ECUACIONES = [
    ("e01", "[parser] llaves de un exponente: `x^{n+1}`", r"x^{n+1}", X ** (N + 1), "="),
    ("e02", "[parser] llaves con resta: `x^{n-1}`", r"x^{n-1}", X ** (N - 1), "="),
    ("e03", "[parser] grupo dentro del argumento de una macro", r"\sqrt{x^{n+1}}",
     math.sqrt(X ** (N + 1)), "="),
    ("e04", "[parser] `\\left( \\right)` con exponente con llaves", r"\left(x^{n-1}\right)^{2}",
     (X ** (N - 1)) ** 2, "="),
    ("e05", "[parser] exponente con suma y potencia dentro", r"2^{x^{2}+1}", 2 ** (X ** 2 + 1), "="),
    ("e06", "[parser] argumento opcional y llaves: `\\sqrt[3]{...}`", r"\sqrt[3]{x^{n+1}}",
     (X ** (N + 1)) ** (1 / 3), "="),
    ("e07", "espacio tras una macro: `a \\cdot b`", r"a \cdot b", A * B, "="),
    ("e08", "dos `\\cdot` seguidos", r"a \cdot b \cdot x", A * B * X, "="),
    ("e09", "relación como expresión: `a \\leq b`", r"a \leq b", A <= B, "="),
    ("e10", "función con argumento que lleva espacios y `\\cdot`", r"\ln(x \cdot a)",
     math.log(X * A), "="),
    ("e11", "comentario `%` dentro de la ecuación (con `=` y `{`)", "x + a % comentario con = y {llave\n",
     X + A, "="),
]

# -------------------------------------------------------------------------------------------
# Casos de algoritmo: (id, qué se prueba, cuerpo, variable que se devuelve, esperado)
# -------------------------------------------------------------------------------------------
ALGORITMOS = [
    ("g01", "[parser] comparaciones escritas tal cual: `<=`, `>=`, `!=`, `==`, `=`", r"""
  \STATE $v \gets 0$
  \IF{$2 <= 3$} \STATE $v \gets v + 1$ \ENDIF
  \IF{$3 >= 3$} \STATE $v \gets v + 2$ \ENDIF
  \IF{$2 != 3$} \STATE $v \gets v + 4$ \ENDIF
  \IF{$3 == 3$} \STATE $v \gets v + 8$ \ENDIF
  \IF{$3 = 3$} \STATE $v \gets v + 16$ \ENDIF
  \IF{$x \leq n$} \STATE $v \gets v + 32$ \ENDIF
  \IF{$a \cdot x \leq b \cdot n$} \STATE $v \gets v + 64$ \ENDIF
  \RETURN $v$
""", "v", 127),
    ("g02", "[parser] `\\FOR` con exponente con llaves: `x^{i-1}`", r"""
  \STATE $w \gets 0$
  \FOR{$i = 1$ \TO $n+1$}
    \STATE $w \gets w + x^{i-1}$
  \ENDFOR
  \RETURN $w$
""", "w", sum(X ** (i - 1) for i in range(1, N + 2))),
    ("g03", "`\\WHILE` con `\\cdot` y `\\leq`", r"""
  \STATE $k \gets 1$
  \STATE $m \gets 0$
  \WHILE{$k \cdot k \leq 50$}
    \STATE $m \gets m + k^{2}$
    \STATE $k \gets k + 1$
  \ENDWHILE
  \RETURN $m$
""", "m", sum(k * k for k in range(1, 8))),
    ("g04", "`\\REPEAT` ... `\\UNTIL` y comentario `%` en una línea de algoritmo", r"""
  \STATE $c \gets 0$ % contador, con = y {llave
  \REPEAT
    \STATE $c \gets c + 1$
  \UNTIL{$c >= n$}
  \RETURN $c$
""", "c", N),
]

ALGORITMOS.append(("g05", "[alias] variable de una letra (`s`) y `\\gets`: el alias no debe romper la macro", r"""
  \STATE $s \gets 0$
  \WHILE{$s \leq 10$}
    \STATE $s \gets s + 3$
  \ENDWHILE
  \RETURN $s$
""", "s", 12))

# \sqrt[3]... y \ln no los entiende el converter original igual de bien: lo que se ve en el
# paquete original en esos casos es una mezcla de parser y converter.


def a_latex(texto):
    """Los trozos entre `comillas` se escriben como código (\\texttt) escapando lo especial."""
    def codigo(m):
        t = m.group(1)
        for a, b in (("\\", "\\textbackslash{}"), ("{", "\\{"), ("}", "\\}"), ("^", "\\^{}"),
                     ("_", "\\_"), ("%", "\\%"), ("~", "\\textasciitilde{}")):
            t = t.replace(a, b)
        return "\\texttt{" + t + "}"
    return re.sub(r"`([^`]*)`", codigo, texto)


def fmt(v):
    return str(v) if isinstance(v, (bool, int)) else f"{v:.6f}"


PREAMBULO = r"""\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{amsmath,amssymb}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage[margin=2.2cm]{geometry}
\setlength{\parindent}{0pt}
\setlength{\abovedisplayskip}{3pt}
\setlength{\belowdisplayskip}{3pt}
\title{Prueba del parser de comPyLaTeX}
\author{}
\date{}
\begin{document}
\maketitle
"""


def bloque_defs():
    L = ["\\section*{Variables que usan las pruebas}"]
    for nombre, valor in DEFS:
        L += ["\\begin{equation}", f"{nombre} = {valor}", f"\\label{{eq:calc:{nombre}}}", "\\end{equation}"]
    L += ["Además, una función:", "\\begin{equation}", "f(t) = t^{n+1}", "\\label{eq:calc:f}",
          "\\end{equation}"]
    return L


def bloque_ecuacion(c):
    cid, que, rhs, esp, simbolo = c
    L = [f"\\textbf{{{cid}}}\\quad {a_latex(que)}\\\\", f"esperado: \\texttt{{{fmt(esp)}}}",
         "\\begin{equation}", f"{cid[0]}_{{{cid[1:]}}} = {rhs}".rstrip("\n"),
         f"\\label{{eq:calc:{cid}}}", "\\end{equation}",
         "\\begin{equation}", f"{cid[0]}_{{{cid[1:]}}} {simbolo}", f"\\label{{eq:res:{cid}}}",
         "\\end{equation}"]
    return L


def bloque_algoritmo(c):
    cid, que, cuerpo, var, esp = c
    return [f"\\textbf{{{cid}}}\\quad {a_latex(que)}\\\\", f"esperado: \\texttt{{{fmt(esp)}}}",
            "\\begin{algorithm}[h]", f"\\caption{{{cid}}}", f"\\label{{alg:calc:{cid}}}",
            "\\begin{algorithmic}", cuerpo.rstrip("\n"), "\\end{algorithmic}", "\\end{algorithm}",
            "\\begin{equation}", f"{cid[0]}_{{{cid[1:]}}} =", f"\\label{{eq:res:{cid}}}",
            "\\end{equation}"]


def documento(ecs, algs, con_titulos=True):
    L = [PREAMBULO] + bloque_defs()
    if ecs:
        L.append("\\section*{Ecuaciones}")
        for c in ecs:
            L += bloque_ecuacion(c)
    if algs:
        L.append("\\section*{Algoritmos}")
        for c in algs:
            L += bloque_algoritmo(c)
    L.append("\\end{document}")
    return "\n".join(L) + "\n"


# Casos que con el parser/converter ORIGINAL no dan un valor erróneo, sino un error que para todo
SOLO_NUEVO = {"g01", "g04", "g05"}


def generar(para_original=False):
    """Con para_original=True se omiten los casos de SOLO_NUEVO: el documento se ejecuta entero
    con el paquete original y los fallos se ven como valores mal calculados, no como excepciones."""
    ecs = [c for c in ECUACIONES if not (para_original and c[0] in SOLO_NUEVO)]
    algs = [c for c in ALGORITMOS if not (para_original and c[0] in SOLO_NUEVO)]
    ruta = os.path.join(AQUI, "test_parser_original.tex" if para_original else "test_parser.tex")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(documento(ecs, algs))
    print(f"Escrito {ruta} ({len(ecs) + len(algs)} pruebas)")


# -------------------------------------------------------------------------------------------
def iguales(esp, texto):
    if isinstance(esp, bool):
        return texto == str(esp)
    if isinstance(esp, int):
        return texto == str(esp)
    try:
        return abs(float(texto) - esp) < 5e-7 * max(1, abs(esp))
    except ValueError:
        return False


def ejecutar_caso(compylatex, cid, ecs, algs):
    ruta = os.path.join(AQUI, "_caso.tex")
    salida = os.path.join(AQUI, "_caso_resultado.tex")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(documento(ecs, algs))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            compylatex(ruta, salida)
    except Exception as e:                      # el paquete falla: se cuenta como fallo del caso
        return None, f"{type(e).__name__}: {str(e)[:90]}"
    with open(salida, encoding="utf-8") as f:
        out = f.read()
    m = re.search(r"=\s*(\S+)\s*\\label\{eq:res:%s\}" % cid, out)
    return (m.group(1) if m else None), "sin resultado insertado"


def verificar(paquete):
    compylatex = importlib.import_module(f"{paquete}.executor").compylatex
    print(f"Paquete: {paquete}")
    fallos = 0
    casos = [(c[0], c[1], c[3], [c], []) for c in ECUACIONES] + \
            [(c[0], c[1], c[4], [], [c]) for c in ALGORITMOS]
    for cid, que, esp, ecs, algs in casos:
        valor, motivo = ejecutar_caso(compylatex, cid, ecs, algs)
        if valor is not None and iguales(esp, valor):
            print(f"  ok     {cid}  {que.replace(chr(96), '')}")
        else:
            fallos += 1
            detalle = f"dio {valor}" if valor is not None else motivo
            print(f"  FALLA  {cid}  {que.replace(chr(96), '')}\n           esperado {fmt(esp)}; {detalle}")
    for nombre in ("_caso.tex", "_caso_resultado.tex"):
        try:
            os.remove(os.path.join(AQUI, nombre))
        except OSError:
            pass
    print(f"{len(casos) - fallos}/{len(casos)} correctos")
    return fallos


if __name__ == "__main__":
    if "--generar" in sys.argv:
        generar(para_original="--para-original" in sys.argv)
    if "--verificar" in sys.argv:
        pkg = sys.argv[sys.argv.index("--paquete") + 1] if "--paquete" in sys.argv else "compylatex"
        sys.exit(1 if verificar(pkg) else 0)
    if len(sys.argv) == 1:
        print(__doc__)