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

# APÉNDICE: cómo trabajar en el proyecto

## Descarga
- Crear cuenta en [github.com](https://github.com).
- Solicitar unirse al proyecto.

**Observación**: proyecto se ha generado con las siguientes propiedades:
- Public
- Add README
- Add .gitignore, Python
- Add license, GPL3
- Creada rama dev en el despegable de ramas

## Modificación del repositorio
- Los cambios se hacen en una _feature_ y se hace _merge_ a _dev_.

## Paso de los cambios a la rama main
- Tras validar los cambios de _dev_, en GitHub ir al menú (superior) Pull requests
- Escoger New pull request
- En base selecciona main
- En compare selecciona dev
- Se muestran los cambios entre dev y main. Si todo está correcto, pulsar Create pull request
- Se añade un mensaje de descripción (opcional) y luego pulsa Merge pull request
- Si no hay conflictos, confirma con Confirm merge. 
- Si la compilación está ligada a la rama main, en Actions se observará un nuevo workflow que actualizará el HTML.

## Trabajo en local

### Modificación del código
- Clonar repositorio: Code, Copy URL
- Instalar Git: https://git-scm.com/downloads
- Abrir CMD, ir a la carpeta de proyecto: git clone https://github.com/fran-pena/python-latex.git
- Cambiar a la rama dev, git checkout dev
- `git pull`, modificar código
- Actualizar repositorio en la nube: `git status`, `git add`, `git commit`, `git push`

### Construcción del HTML
- Instalar Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- En un CMD, ir a una carpeta; por ejemplo, el HOME del usuario, _C:\\Users\\<usuario>\\_
- Crear entorno venv, `python -m venv jupyter_venv`
- Entrar en el entorno, `jupyter_venv/Scripts/activate`
- En la carpeta del proyecto, instalar los requisitos:
```shell
   python -m pip install -r requirements.txt
```   
- En el proyecto, crear el fichero _.vscode/settings.json_ con el contenido:
```json
{
    "python.defaultInterpreterPath": "C:/Users/<usuario>/jupyter_venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```
donde <usuario> es el usuario en el que se ha creado el venv. Comprobar que es la rtuta correcta.
- Ejecutar: `jupyter-book build . --all`

### Registrar el kernel del venv
Si se trabaja con VS Code, es recomendable registrar el kernel del venv:
```shell
jupyter_venv\Scripts\activate
python -m pip install ipykernel
python -m ipykernel install --user --name=jupyter_venv --display-name="Python (jupyter_venv)"
```
## TRabajo en la nube

### Modificaciones en la nube
- Ir a [https://colab.research.google.com/](https://colab.research.google.com/)
- En Abrir cuaderno - GitHub, escribir: nombre de usuario de Github, repositorio python-latex y rama dev.
- Hacer modificaciones en el fichero IPYNB
- Ir a Archivo - Guardar (no pulsar en Gist!), dar permisos para acceder a la cuenta de GitHub.

Las personas que no pertenecen al proyecto, aún pueden observar los IPYNB de un proyecto público obteniendo su dirección URL y sustituyendo el inicio https://github.com/ por https://colab.research.google.com/github/. Por ejemplo, sustituyendo:

https://github.com/fran-pena/python-latex/blob/dev/Parte1.ipynb

por 

https://colab.research.google.com/github/fran-pena/python-latex/blob/dev/Parte1.ipynb

### Construcción del HTML  en la nube
- Crear en el repositorio el fichero _.github/workflows/build-book.yml_. Las partes principales son:
- Indicación de la rama que desencadena la compilación del HTML (cambiar temporalmente a dev para las pruebas)
```yaml
on:
  push:
    branches: [main]
```
**Atención:** GitHub Actions solo permite 2.000 minutos al mes; cada compilación es un minuto. Para evitarlas, volver a compilación desde main.

  - Indicación de los paquetes Python a instalar:
```shell
run: |
  pip install -U pip
  pip install jupyter-book
  pip install sympy
```          

- Modificar algún IPYNB de la rama dev con Google Colab.
- La primera vez, se debe comprobar que se ha creado la rama gh-pages.
- Tras la creación automática de la rama gh-pages, ir a Settings - Pages - Build and Depolyment - Source, escoger Deploy from a branch y escoger gh-pages.
- Ir al menú (superior) Actions - All workflows. Se listan todas las compilaciones generadas. Al entrar en cada una se puede ver si ha habido errores.

### Lectura del HTML en la nube
- Si la compilación fue existosa, el resultado se puede ver en [https://fran-pena.github.io/python-latex/intro.html](https://fran-pena.github.io/python-latex/intro.html)

# ToDo
- Quarto permite latex más complejo que Jupyter NB.
  - Pro: Posit Cloud es equivalente a Google Colab
  - Con: No he conseguido usar el paquete algorithmic
  - Con: los fichero qmd no son interactivos: se editan como md y se compilan en html o PDF.
  - Con: el latex complejo parece solo compilarse para PDF, no para HTML (inutiliza la compartición por Google Pages), a menos que solo se cuegue el PDF.

- Como alternativa, leer ficheros tex, identificar ecuaciones por label y generar el resultado.
- TODO: pensar cómo organizar la salida: 
  - valores: tener una ecuación $$v\label{eq:res:1}$$, detectar el v y poner v = ... (identificar si es escalar, vector o matrix)
  - Gráficas: tener una figure, detectar el label{plot:res:...} y leer la ruta del fichero y ponerlo ahí. Dentro de la gráfica debemos poner un comentario tipo %plot(u,v) 

