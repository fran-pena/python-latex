# Handoff: algoritmos reutilizables con REQUIRE

## Git y versión

- Repositorio: `github`, rama de trabajo `feature/require`, creada desde `dev`
  y publicada en `origin`.
- Se promovió el contenido previo de `dev` a `main`, se estableció la versión
  `1.0.0` en `compylatex/pyproject.toml` y se creó la etiqueta anotada `v1.0.0`.
  `main` y `dev` se publicaron junto con la etiqueta. El commit base es
  `6f0701a`.
- La etiqueta contiene el código anterior a esta funcionalidad; no constituye
  una publicación en PyPI ni una certificación de calidad.
- La rama de desarrollo aún conserva `1.0.0` en los metadatos. Antes de
  distribuir esta rama deberá decidirse una versión diferente: el nuevo
  comportamiento es incompatible con algunos documentos de la 1.0.0. El wheel
  construido durante la comprobación es solo una prueba y no debe publicarse
  como la versión 1.0.0.

## Decisión funcional

El usuario decidió que cualquier `alg:calc` con `\REQUIRE` declare una función,
aunque antes `\REQUIRE` fuera solamente documental. `alg:def` también declara
una función y requiere al menos un `\REQUIRE`. La etiqueta identifica la función;
el cuerpo se ejecuta al llamarla en una expresión posterior. Un `alg:calc` sin
`\REQUIRE` conserva la ejecución inmediata.

Esto rompe el comportamiento anterior de los documentos con `alg:calc` y
`\REQUIRE`: ahora necesitan una llamada explícita y un `eq:calc` para almacenar
el resultado. Los comandos LaTeX permanecen en el documento y continúan
mostrándose al compilarlo. `\ENSURE` no tiene efectos de ejecución.

## Implementación

- `src/compylatex/parser.py`: extrae las listas de parámetros y valida una
  variable por cada `\RETURN`; construye el árbol con alias locales.
- `src/compylatex/executor.py`: registra funciones, comprueba la aridad y crea un
  espacio nuevo para cada llamada. Las dependencias deben pasar por argumentos,
  salvo `math`. Las asignaciones locales no cambian las variables del documento;
  no se realiza copia profunda de objetos mutables.
- `src/compylatex/converter.py`: evita sustituir fragmentos de identificadores
  en los alias locales y en expresiones que invocan estas funciones.
- `examples/secante_require.tex`: un único algoritmo de secante se aplica a
  `f(x)=x^2-2` y `g(x)=x^3-2`. No garantiza convergencia si se alcanza el
  máximo de iteraciones; un denominador cero produce un error.
- `tests/test_require.py`: pruebas con `unittest`.
- `README.md`: contrato, migración y advertencia de seguridad.

La primera fase admite argumentos posicionales, incluidos objetos invocables,
y una única variable por `\RETURN`. No admite prosa en `\REQUIRE`, expresiones
en `\RETURN` ni salidas múltiples en el nuevo modo. Si una ruta termina sin
`RETURN`, se informa con un error. El ámbito local no protege frente a archivos
LaTeX no confiables ni a mutaciones realizadas por los objetos recibidos.

La sustitución de alias en el resto del código preexistente sigue siendo
principalmente textual. Los parámetros de funciones declaradas mediante
ecuaciones conservan las limitaciones preexistentes del conversor. No se ha
rediseñado el sistema global de alias.

## Validación efectuada

- `python -m unittest discover -s tests -v`, con `PYTHONPATH=src`: nueve pruebas
  aprobadas usando el `.venv` de `articulo` con `pylatexenc` instalado.
- Ejecución del ejemplo de la secante con salida independiente: se obtuvieron
  aproximadamente `1.414214` y `1.259921`, y se conservó `\REQUIRE`.
- Ejecución de `examples/calculo.tex` con un archivo de salida independiente:
  llegó hasta el final. No se ha certificado toda la semántica matemática de
  sus ejemplos ni corregido el soporte antiguo de retornos múltiples.
- `pip wheel --no-deps` construyó un wheel en un directorio de sesión con
  aislamiento de compilación; se inspeccionó su contenido. `pyproject.toml`
  incorpora `README`, la versión mínima Python y la licencia. Se mantiene la
  estructura estándar `src`; el paquete es un subdirectorio del repositorio.
- Las comprobaciones se realizaron con Python 3.14.4; quedan pendientes otras
  versiones compatibles y la validación del proceso de publicación en PyPI.

## Contexto adicional

La decisión de compatibilidad y su evolución están documentadas en
`../../articulo/conversa/etiquetas_funcion.md`. La copia de texto del TFG está
en `../../articulo/doc/Herramientas_para_cientificos_no_programadores.txt`; los
ejemplos están en el capítulo 3 y la discusión de `\REQUIRE` y `\ENSURE` en
la sección 4.2.
