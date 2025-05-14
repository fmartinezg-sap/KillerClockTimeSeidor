# KillerClockTimeSeidor

KillerClockTimeSeidor es una aplicación de gestión y automatización de tareas programadas con interfaz gráfica, persistencia en base de datos y notificaciones en el sistema.

## Funcionalidad principal

- **Gestión de tareas programadas**: Permite crear, consultar y eliminar tareas que se ejecutan de forma periódica según la configuración del usuario.
- **Persistencia**: Todas las tareas se guardan en una base de datos SQLite local, asegurando que persisten entre sesiones.
- **Interfaz gráfica moderna**: Utiliza PySide6 (Qt) para ofrecer una experiencia visual intuitiva y cómoda.
- **Notificaciones**: Informa al usuario mediante mensajes en el área de notificación (system tray) cuando una tarea se ejecuta o finaliza.
- **System tray**: La aplicación se ejecuta en segundo plano y se controla desde el icono de la bandeja del sistema, permitiendo acceso rápido a la gestión de tareas.
- **Reloj en tiempo real**: Muestra la hora actual en formato `DD/MM/AAAA HH:MM:SS` y se actualiza cada segundo en la ventana de lista de tareas.
- **Visualización clara de tareas**: Cada tarea muestra:
  - Descripción
  - Fecha y hora de inicio y fin
  - Intervalo de ejecución
  - Próxima ejecución
  - Número de ejecuciones realizadas y totales
- **Refresco automático**: El listado de tareas se actualiza automáticamente cada segundo.
- **Control manual**: Botón para refrescar la lista manualmente y botones para crear o eliminar tareas.

## Uso básico

1. **Arranca la aplicación** ejecutando `main.py`.
2. El icono de la aplicación aparecerá en la bandeja del sistema.
3. Haz clic derecho en el icono para acceder a:
   - "Ver tareas": Abre la ventana con el listado de tareas activas y controles.
   - "Nueva tarea": Abre la ventana para crear una nueva tarea.
   - "Salir": Cierra la aplicación.
4. **Crear una tarea**:
   - Pulsa "Crear tarea" en la ventana de tareas o desde el menú del tray.
   - Rellena la descripción, selecciona fechas, intervalo y número de ejecuciones.
   - Por defecto, la fecha/hora de inicio y fin es la actual.
   - Guarda la tarea.
5. **Eliminar una tarea**:
   - Selecciona una tarea en la lista y pulsa "Eliminar tarea seleccionada".
   - La tarea se elimina del sistema y de la base de datos.
6. **Ejecución y notificaciones**:
   - Las tareas se ejecutan automáticamente según lo programado.
   - Se muestran notificaciones en el sistema cada vez que una tarea se ejecuta o finaliza.
   - El contador de ejecuciones y la próxima ejecución se actualizan en tiempo real.

## Tecnologías utilizadas
- Python 3
- PySide6 (Qt)
- APScheduler
- SQLite3
- pytz y python-dateutil (gestión de fechas)

## Estructura del proyecto
- `main.py`: Punto de entrada de la aplicación.
- `task.py`: Modelo de datos de tareas.
- `task_database.py`: Lógica de persistencia con SQLite.
- `task_config_window.py`: Ventana para crear/editar tareas.
- `task_list_window.py`: Ventana para visualizar y gestionar tareas activas.
- `task_daemon.py`: Lógica principal de gestión, scheduling y notificaciones.

## Requisitos
- Python 3.8+
- Instalar dependencias con:
  ```
  pip install -r requirements.txt
  ```

## Notas
- La aplicación está pensada para ejecutarse en segundo plano y ser poco intrusiva.
- Todas las fechas se muestran en formato `DD/MM/AAAA HH:MM:SS`.
- El refresco de la lista de tareas es automático y no requiere intervención manual.

---

¿Tienes alguna duda o necesitas ayuda con la configuración o el uso? ¡Contacta al desarrollador o revisa el código fuente para más detalles!
