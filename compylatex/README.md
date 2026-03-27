# compylatex

Ejecuta algoritmos embebidos en LaTeX y devuelve el documento completado con los resultados.

## Instalación
```bash
pip install -e .
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
Los entornos `algorithmic` se ejecutan en el orden en que aparecen.

## Ejemplo
```bash
cd examples
python -c "import compylatex as cl; cl.compylatex('calculo.tex', 'calculo_resultado.tex')"
```

## Requisitos

- Python 3.10+
- pylatexenc >= 2.10