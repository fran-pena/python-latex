# Guía de uso de ComPyLaTeX

## Idea general

ComPyLaTeX permite incluir cálculos y algoritmos en un documento LaTeX y
obtener otro documento `.tex` con los resultados insertados. El documento
conserva sus ecuaciones, algoritmos y etiquetas; después puede compilarse
normalmente para obtener un PDF.

El usuario señala qué partes deben procesarse mediante `\label`. A grandes
rasgos, ComPyLaTeX lee el documento de principio a fin, traduce los cálculos
reconocidos a Python y guarda los valores y funciones para utilizarlos más
adelante. Cuando encuentra una etiqueta de resultado, recoge el valor disponible
en ese punto y lo inserta en el documento de salida.

Esta guía resume la filosofía de etiquetado del capítulo 2 del TFG, adaptada
al comportamiento actual del paquete.

No todos los entornos o expresiones LaTeX son ejecutables. En particular, los
cálculos de esta guía se escriben en entornos `equation`; los algoritmos usan
`algorithm` con `algorithmic` en su interior.

## Requisitos e instalación

Se necesita Python 3.10 o posterior y la dependencia `pylatexenc`. La instalación
editable desde la carpeta `compylatex` instala el paquete y su dependencia:

```shell
python -m pip install -e .
```

Utiliza el Python de tu entorno virtual para instalar y ejecutar el paquete. Si
trabajas en PowerShell sin activar el entorno, puedes invocar directamente su
intérprete con `& "ruta\al\entorno\Scripts\python.exe"` en lugar de `python`.

El documento LaTeX debe incluir, entre otros, los paquetes utilizados por los
ejemplos:

```latex
\usepackage{amsmath}
\usepackage{algorithm}
\usepackage{algorithmic}
```

Para obtener un PDF también se necesita una distribución de LaTeX con esos
paquetes. ComPyLaTeX genera el `.tex`; no compila el PDF.

## Qué significan las etiquetas

Las etiquetas reconocidas tienen tres componentes:

```text
entorno:tipo:nombre
```

| Etiqueta | Propósito |
| --- | --- |
| `eq:calc:nombre` | Calcula una variable o define una función matemática. |
| `eq:res:nombre` | Inserta el valor almacenado con ese nombre. |
| `alg:calc:nombre` | Ejecuta un algoritmo sin `\REQUIRE`; con `\REQUIRE`, define una función reutilizable. |
| `alg:def:nombre` | Define explícitamente una función reutilizable y requiere `\REQUIRE`. |

`nombre` es un identificador interno, también llamado *alias*. Para evitar
problemas, usa nombres distintos formados por letras y números, que empiecen por
una letra, como `toldic` o `raizuno`. El alias de una función reutilizable debe
ser un identificador válido de Python y no puede ser `math` ni una palabra
reservada de Python.

Los entornos sin una etiqueta reconocida no se procesan. La etiqueta de
`algorithm` puede situarse en ese entorno o dentro de su `algorithmic`.

### Datos y resultados

Una ecuación de cálculo asigna el valor de su lado derecho al alias de la
etiqueta. Por ejemplo:

```latex
\begin{equation}
    tol_{dic} = 1e-6
    \label{eq:calc:toldic}
\end{equation}
```

Aquí `tol_{dic}` es el nombre escrito en el documento y `toldic` es su alias
interno. Ese valor puede utilizarse en cálculos posteriores.

Para mostrar un valor, escribe una ecuación con el lado derecho vacío:

```latex
\begin{equation}
    tol_{dic} =
    \label{eq:res:toldic}
\end{equation}
```

El nombre de `eq:res` debe coincidir con el alias calculado antes. La etiqueta
debe ir después del signo `=`, separada solo por espacios o saltos de línea.
Si el alias no se ha calculado, el programa muestra una advertencia y no inserta
un valor. Para volver a procesar un documento, parte del original con el hueco
vacío: los resultados ya escritos no se sustituyen automáticamente.

### Funciones matemáticas en ecuaciones

Una ecuación como la siguiente define una función que puede llamarse más de una
vez:

```latex
\begin{equation}
    f(x) = x^2 - 2
    \label{eq:calc:f}
\end{equation}

\begin{equation}
    valor = f(2)
    \label{eq:calc:valor}
\end{equation}
```

Para las funciones definidas de este modo, utiliza el mismo nombre en la
ecuación y en la etiqueta, como `f` en el ejemplo. Los argumentos se indican
entre paréntesis y separados por comas. Para mostrar `valor`, añade una
ecuación `eq:res:valor` con el lado derecho vacío.

### Algoritmos de ejecución inmediata

Un algoritmo `alg:calc` sin `\REQUIRE` se ejecuta cuando aparece. Puede utilizar
los datos definidos anteriormente y modificar variables del espacio de cálculo
compartido:

```latex
\begin{equation}
    b = 3
    \label{eq:calc:b}
\end{equation}

\begin{algorithm}
\label{alg:calc:resultado}
\begin{algorithmic}
    \STATE $resultado = 2 \cdot b$
    \RETURN $resultado$
\end{algorithmic}
\end{algorithm}

\begin{equation}
    resultado =
    \label{eq:res:resultado}
\end{equation}
```

En este modo, la etiqueta del algoritmo identifica el alias asociado a su
variable de retorno. Para los casos sencillos, utiliza una única variable en
`\RETURN` y el mismo alias en `eq:res`.

### Algoritmos reutilizables con `\REQUIRE`

Si un algoritmo `alg:calc` contiene `\REQUIRE`, se registra como función y
**no se ejecuta al declararlo**. También se puede usar `alg:def` para indicar
explícitamente que es una definición. La parte final de la etiqueta es el
nombre de la función:

```latex
\begin{algorithm}
\label{alg:def:doble}
\begin{algorithmic}
    \REQUIRE $x$
    \STATE $y = 2 \cdot x$
    \RETURN $y$
\end{algorithmic}
\end{algorithm}

\begin{equation}
    primer = doble(3)
    \label{eq:calc:primer}
\end{equation}

\begin{equation}
    segundo = doble(5)
    \label{eq:calc:segundo}
\end{equation}

\begin{equation}
    primer =
    \label{eq:res:primer}
\end{equation}

\begin{equation}
    segundo =
    \label{eq:res:segundo}
\end{equation}
```

- `\REQUIRE` enumera las entradas posicionales, separadas por comas y en el
  orden de la llamada. Puede haber varias líneas `\REQUIRE`; se admiten nombres
  de variables, no descripciones en prosa.
- Las entradas pueden ser números o funciones matemáticas definidas previamente.
- Cada llamada dispone de sus propios parámetros y variables de trabajo. Los
  datos externos que necesite el algoritmo deben pasarse como argumentos.
- `\RETURN` debe indicar una única variable, no una expresión ni varias
  variables. Si la ejecución termina sin alcanzar un `\RETURN`, se produce un
  error.
- `\ENSURE` es documental: se conserva en el LaTeX, pero no declara salidas ni
  se comprueba como condición.

Los argumentos mutables no se copian: aislar las asignaciones locales no impide
que una función recibida como argumento modifique sus propios datos.

**Compatibilidad:** en documentos anteriores, `\REQUIRE` podía ser solo
documental. Ahora cambia el significado de `alg:calc`: el nombre de la etiqueta
identifica la función, y para obtener un resultado hay que llamarla en una
ecuación posterior. Los algoritmos sin `\REQUIRE` mantienen la ejecución
inmediata.

## Ejecutar un documento

En Python, indica el archivo de entrada y, preferiblemente, uno distinto para
la salida:

```python
import compylatex as cl

cl.compylatex("documento.tex", "documento_resultado.tex")
```

La función escribe el documento de salida con los resultados disponibles. Si
el archivo de salida ya existe, lo sobrescribe.
Después puedes compilar `documento_resultado.tex` con tu herramienta LaTeX
habitual. Las rutas de este ejemplo se resuelven desde el directorio de trabajo.

**Atención:** si se omite el segundo argumento, ComPyLaTeX sobrescribe el archivo
de entrada:

```python
cl.compylatex("documento.tex")
```

Utiliza solo documentos de confianza: ComPyLaTeX ejecuta código derivado del
contenido del archivo. Las variables locales de las funciones reutilizables no
constituyen una barrera de seguridad.

## Ejemplos incluidos

En [`examples/`](../examples/) se pueden consultar:

- [`calculo.tex`](../examples/calculo.tex): cálculos y algoritmos, incluidos
  dicotomía, Newton–Raphson, Jacobi, Euler y número combinatorio. Su salida de
  referencia es [`procesado_calculo.tex`](../examples/procesado_calculo.tex);
  también se proporcionan los PDF correspondientes.
- [`secante_require.tex`](../examples/secante_require.tex): define una vez el
  método de la secante y lo llama con dos funciones distintas. Puede devolver
  la última aproximación sin converger si se alcanza el límite de iteraciones.

Por ejemplo, desde la carpeta `compylatex`:

```python
import compylatex as cl

cl.compylatex("examples/calculo.tex", "examples/calculo_resultado.tex")
cl.compylatex("examples/secante_require.tex", "examples/secante_resultado.tex")
```

Elige rutas de salida que no existan o que puedas sobrescribir. No es necesario
sobrescribir las fuentes ni volver a procesar archivos ya completados.

## Pruebas

El paquete incluye pruebas en [`tests/test_require.py`](../tests/test_require.py).
Cubren, entre otros casos, el uso de `\REQUIRE`, llamadas repetidas, el ejemplo
de la secante y un algoritmo de ejecución inmediata.

Una vez instalado el paquete, ejecútalas desde la carpeta `compylatex` con el
mismo intérprete del entorno virtual:

```shell
python -m unittest discover -s tests -v
```

Un resultado final `OK` indica que todas las pruebas ejecutadas han pasado.
Estas pruebas no certifican todas las expresiones LaTeX ni todos los algoritmos
posibles.

## Limitaciones prácticas

- El traductor admite solo un subconjunto de expresiones y comandos LaTeX; una
  ecuación visualmente válida no es necesariamente ejecutable.
- La sustitución de alias es principalmente textual: evita nombres ambiguos y
  comprueba los resultados, especialmente si unos nombres contienen a otros.
- La compatibilidad con retornos múltiples de algoritmos requiere revisión.
- ComPyLaTeX no calcula automáticamente derivadas ni garantiza la convergencia
  de los métodos numéricos que se escriban en el documento.
