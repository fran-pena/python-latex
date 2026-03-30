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
- Los entornos `algorithmic` se ejecutan en el orden en que aparecen.

## Ejemplo
Aquí se muestra el [documento LaTeX original](../compylatex/examples/calculo.tex) y su [compilación en PDF](../compylatex/examples/calculo.pdf).

Aquí se muestra el [resultado compilado en PDF](../compylatex/examples/calculo_result.pdf), tras usar el paquete **compylatex**.
