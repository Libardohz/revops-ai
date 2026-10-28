# Diseño de PWA para Gestión de Tareas

## Objetivo
Construir una Aplicación Web Progresiva (PWA) optimizada para móviles para la gestión de tareas y actividades. Funcionará localmente utilizando `localStorage` (fase Beta) y permitirá a los usuarios exportar tareas a sus calendarios nativos.

## Arquitectura
- **Framework**: React usando Vite
- **Estilos**: CSS puro (Vanilla) con estética moderna (efecto cristal o *glassmorphism*, micro-animaciones, sensación de alta gama)
- **Almacenamiento de Datos**: `localStorage` (Navegador)
- **Despliegue**: Configurada como PWA (manifest.json, service worker) para que pueda instalarse en las pantallas de inicio de iOS/Android.

## Componentes
1. **Contenedor de la Aplicación**: Gestiona el estado global (lista de tareas) y la solicitud de instalación de la PWA.
2. **Lista de Tareas**: Muestra las tareas pendientes y completadas.
3. **Elemento de Tarea**: Muestra los detalles de la tarea (Nombre, Tipo, Urgencia, Fecha). Incluye una casilla para marcarla como completada y un botón para exportarla a Google/Apple Calendar.
4. **Formulario de Tarea**: Ventana modal o sección desplegable que contiene:
   - Nombre (entrada de texto)
   - Tipo (desplegable: Trabajo, Personal, Estudio, Otro)
   - Urgencia (desplegable: Alta, Media, Baja)
   - Fecha y Hora (entrada de tipo datetime-local)

## Flujo de Datos
- El usuario llena el formulario -> la función `addTask` actualiza el estado de React -> `useEffect` guarda el nuevo estado en `localStorage`.
- Al cargar por primera vez -> `useEffect` lee de `localStorage` y establece el estado de React.
- Exportar al Calendario -> Genera un archivo `.ics` (Apple) o un enlace web de Google Calendar dinámicamente basado en los datos de la tarea.
