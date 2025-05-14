# KillerClockTimeSeidor

Aplicación de control de tiempo para Seidor.

## Descripción

Esta aplicación permite gestionar y controlar el tiempo dedicado a diferentes tareas y proyectos.

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`

## Uso

Para ejecutar la aplicación:

```bash
uvicorn main:app --reload
```

## Estructura del Proyecto

```
.
├── main.py           # Punto de entrada de la aplicación
├── requirements.txt  # Dependencias del proyecto
├── src/              # Código fuente
└── tests/            # Tests unitarios y de integración
```

## Contribución

1. Crear una rama para tu feature
2. Realizar cambios
3. Crear pull request