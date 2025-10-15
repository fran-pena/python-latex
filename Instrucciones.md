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

# APÉNDICE I: Instrucciones para trabajar con Python-LaTeX
- Crear cuenta en github.com

## Creación del respositorio en github
- Crear nuevo proyecto: pithon-latex
   Public
   Add README
   Add .gitignore, Python
   Add license, GPL3
- Crear rama dev, en el despegable de ramas.

## Modificaciones en local   
- Clonar repositorio: Code, Copy URL
- Instalar Git: https://git-scm.com/downloads
- Abrir CMD, ir a la carpeta de proyecto: git clone https://github.com/fran-pena/python-latex.git
- Cambiar a la rama dev, git checkout dev
- git pull, modificar código
- Actualizar repositorio en la nube: git status, git add, git commit, git push

## Compilación del HTML en local
- Instalar Python: https://www.python.org/downloads/
- Crear entorno venv, python -m venv jupyter_venv
- Entrar en el entorno, jupyter_venv/Scripts/activate
- Instalar paquetes de jupyter-book
   python -m pip install jupyter-book
   python -m pip install jupyter-cache
   python -m pip install plotly
   python -m pip install ipywidgets
   python -m pip install matplotlib
   python -m pip install numpy
   python -m pip install pandas

## Modificaciones en la nube
- Ir a https://colab.research.google.com/
- En Abrir cuaderno - GitHub, escribir: nombre de usuario de Github, repositorio python-latex y rama dev.
- Hacer modificaciones en el fichero IPYNB
- Ir a Archivo - Guardar (no pulsar en Gist!), dar permisos para acceder a la cuenta de GitHub.

Las personas que no pertenecen al proyecto, aún pueden observar los IPYNB de un proyecto público obteniendo su dirección URL y sustituyendo el inicio https://github.com/ por https://colab.research.google.com/github/. Por ejemplo, sustituyendo:

https://github.com/fran-pena/python-latex/blob/dev/Parte1.ipynb

por 

https://colab.research.google.com/github/fran-pena/python-latex/blob/dev/Parte1.ipynb

## Compilacion en la nube
- Crear en el repositorio el fichero .github/workflows/build-book.yml. Las partes principales son:
  - Indicación de la rama que desencadena la compilación del HTML (cambiar temporalmente a dev para las pruebas)
```
on:
  push:
    branches: [main]
```
**Atención:** GitHub Actions solo permite 2.000 minutos al mes; cada compilación es un minuto. Para evitarlas, volver a compilación desde main.

  - Indicación de los paquetes Python a instalar:
```
run: |
  pip install -U pip
  pip install jupyter-book
  pip install sympy
```          

- Modificar algún IPYNB de la rama dev con Google Colab.
- La primera vez, se debe comprobar que se ha creado la rama gh-pages.
- Tras la creación autom´tica de la rama gh-pages, ir a Settings - Pages - Build and Depolyment - Source, escoger Deploy from a branch y escoger gh-pages.
- Ir al menú (superior) Actions - All workflows. Se listan todas las compilaciones generadas. Al entrar en cada una se puede ver si ha habido errores.

## Lectura del HTML en la nube
- Si la compilación fue existosa, el resultado se puede ver en

https://fran-pena.github.io/python-latex/intro.html

## Paso de los cambios a la rama main
- Tras validar los cambios de dev, en GitHub ir al menú (superior) Pull requests
- Escoger New pull request
- En base selecciona main
- En compare selecciona dev
- Se muestran los cambios entre dev y main. Si todo está correcto, pulsar Create pull request
- Se añade un mensaje de descripción (opcional) y luego pulsa Merge pull request
- Si no hay conflictos,  confirma con Confirm merge. 
- Si la compilación está ligada a la rama main, en Actions se observará un nuevo workflow que actualizará el HTML.
