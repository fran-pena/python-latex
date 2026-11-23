# compylatex

Ejecuta algoritmos embebidos en LaTeX y devuelve el documento completado con los resultados.

Consulta la [guía de uso](docs/guia_de_uso.md) para entender las etiquetas,
ejecutar documentos, consultar los ejemplos y ejecutar las pruebas.

## Instalación

Desde la carpeta `compylatex`, usando el intérprete de tu entorno virtual:

```bash
python -m pip install -e .
```

## Uso
```python
import compylatex as cl

cl.compylatex("calculo.tex")                       # sobreescribe el original
cl.compylatex("calculo.tex", "calculo_result.tex") # escribe en fichero nuevo
```

## Convenciones en el .tex

Las ecuaciones con `\label{eq:calc:nombre}` se evalúan como cálculos.
Las ecuaciones con `\label{eq:res:nombre}` se completan con el resultado.
Los algoritmos `alg:calc` sin `\REQUIRE` se ejecutan en el orden en que aparecen.

## Algoritmos reutilizables

Un algoritmo `alg:calc` que contiene `\REQUIRE` se registra como función y no
se ejecuta hasta que se invoca. También puede declararse explícitamente con
`alg:def`. El último componente de la etiqueta es el nombre de la función.

```latex
\begin{algorithm}
\label{alg:calc:doble}
\begin{algorithmic}
    \REQUIRE $x$
    \STATE $y = 2 \cdot x$
    \RETURN $y$
\end{algorithmic}
\end{algorithm}

\begin{equation}
    resultado = doble(3)
    \label{eq:calc:resultado}
\end{equation}

\begin{equation}
    resultado =
    \label{eq:res:resultado}
\end{equation}
```

`\REQUIRE` declara argumentos posicionales, en orden, separados por comas;
puede aparecer varias veces. Admite valores numéricos y funciones definidas
previamente. `\RETURN` devuelve una sola variable; sus expresiones y retornos
múltiples todavía no están soportados en este modo. Los argumentos y
asignaciones son locales a cada llamada. Las funciones recibidas pueden tener
su propio estado y no se copian los objetos mutables pasados por el usuario.
Las dependencias deben proporcionarse como argumentos; `math` está disponible
para las operaciones matemáticas. `\ENSURE` permanece exclusivamente
documental y no se comprueba.

La función está disponible después de su declaración y se llama desde una
ecuación `eq:calc` o desde expresiones compatibles del documento. Los comandos
originales `\REQUIRE` y `\ENSURE` se conservan en el archivo LaTeX, por lo que
siguen apareciendo al compilarlo normalmente.

**Cambio incompatible:** antes, un `\REQUIRE` en `alg:calc` solo describía el
algoritmo; ahora lo convierte en función. La etiqueta deja de nombrar la salida
inmediata y la ejecución debe hacerse mediante una llamada explícita. Los
documentos existentes que incluyan `\REQUIRE` deberán adaptarse. Los algoritmos
sin `\REQUIRE` conservan la ejecución inmediata.

Véase [el ejemplo de la secante](examples/secante_require.tex), que aplica
un mismo algoritmo a dos funciones. Al alcanzar el límite de iteraciones, este
ejemplo devuelve la última aproximación sin garantizar la convergencia.

ComPyLaTeX ejecuta código derivado del documento: utilícese únicamente con
archivos LaTeX de confianza. El ámbito local no es una barrera de seguridad.

## Ejemplo
```bash
cd examples
python -c "import compylatex as cl; cl.compylatex('calculo.tex', 'calculo_resultado.tex')"
```

## Pruebas

Desde la carpeta `compylatex`, con el paquete instalado:

```bash
python -m unittest discover -s tests -v
```

## Web
La rama dev de este repositorio puede probarse en [compylatex.streamlit.app](https://compylatex.streamlit.app/).

## Requisitos

- Python 3.10+
- pylatexenc >= 2.10