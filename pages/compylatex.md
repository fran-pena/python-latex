---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
# El paquete compylatex

Este apartado muestra un ejemplo de uso del paquete **compylatex**. Este paquete ejecuta ecuaciones y algoritmos embebidos en un documento LaTeX y devuelve el documento completado con los resultados.

## Instalación
Véase el [README.md del paquete](../compylatex/README.md).

## Uso
```python
import compylatex as cl

cl.compylatex("calculo.tex")                       # sobreescribe el original
cl.compylatex("calculo.tex", "calculo_result.tex") # escribe en fichero nuevo
```

## Convenciones en el .tex

- Las ecuaciones con `\label{eq:calc:nombre}` se evalúan como cálculos.
- Las ecuaciones con `\label{eq:res:nombre}` se completan con el resultado.
- Los algoritmos `alg:calc` sin `\REQUIRE` se ejecutan en el orden en que aparecen.

## Algoritmos reutilizables con `\REQUIRE`

Un algoritmo `alg:calc` con `\REQUIRE` define una función reutilizable en lugar
de ejecutarse al aparecer. También puede declararse con `alg:def`; el nombre
de la etiqueta identifica la función. Cada `\REQUIRE` indica sus argumentos
posicionales y `\RETURN` debe indicar una única variable de salida. Para
obtener un resultado, se llama a la función en una ecuación `eq:calc`.

Por ejemplo, el [método de la secante](../compylatex/examples/secante_require.tex)
define una función que se llama dos veces con funciones matemáticas distintas.
La [guía de uso](../compylatex/docs/guia_de_uso.md) explica cómo declararla y
utilizar sus resultados.

**Compatibilidad:** un `\REQUIRE` que antes solo documentaba un `alg:calc`
ahora lo convierte en función. Esos documentos necesitan una llamada explícita
para ejecutar el algoritmo. `\ENSURE` sigue siendo exclusivamente documental.

## Ejemplo
Aquí se muestra el [documento LaTeX original](../compylatex/examples/calculo.tex) y su [compilación en PDF](../compylatex/examples/calculo.pdf).

Aquí se muestra el [resultado compilado en PDF](../compylatex/examples/procesado_calculo.pdf), tras usar el paquete **compylatex**.
