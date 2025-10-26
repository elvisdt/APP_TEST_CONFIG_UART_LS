# UI Blueprint – Configurador QC1

Este documento resume la estructura propuesta para cubrir la configuracion integral del equipo LTE (entradas, salidas, mensajes y tiempos) tomando como referencia el proyecto "PROYECTO ALARMA COMUNITARIA VOX LTE v03".

## Navegacion principal
- **Dashboard**: Resumen del estado del equipo, comunicaciones activas, accesos directos y checklist.
- **Contactos**: Gestion de numeros autorizados, predeterminados y exportacion/importacion CSV.
- **Automatizacion**: Tablas para mapear entradas y salidas, pruebas rapidas y programacion de horarios.
- **Audio**: Inventario de slots, control de reproduccion, carga de archivos y opciones de cifrado.
- **Servidor**: Parametros de conexion (MQTT/TCP/HTTP), credenciales y prueba rapida.
- **Notificaciones**: Canales habilitados, grupos de WhatsApp/app movil y plantillas de mensajes.
- **Logs**: Consola para diagnosticos en tiempo real.

## Lineamientos de diseno
- **Cards reutilizables** (`app/ui/widgets/card.py`) para agrupar zonas logicas (estado, acciones, formularios).
- **Paleta moderna** (`app/ui/styles/styles.py`) con acentos azul LS, fondos claros y controles redondeados.
- **Acciones contextualizadas**: Cada pagina ofrece botones de "Aplicar" y "Restaurar" para alinearse con flujos tipo Teltonika/Queclink.
- **Datos pre-cargados**: Se ofrecen placeholders coherentes (nombres de entradas, grupos, horarios) para acelerar pruebas en campo.

## Integracion futura
- Conectar las señales expuestas en `PageAutomation` y `PageNotifications` a los controladores backend para almacenar/leer configuraciones.
- Sincronizar los atajos del Dashboard con la navegacion (`MainWindow._on_page_requested`).
- Mapear los botones de prueba (salidas, grupos) a acciones MQTT/WhatsApp reales.
- Sustituir los valores hardcodeados del Dashboard por lecturas en vivo (status MQTT, bateria, etc.).

## Referencias
- Codigo: `app/ui/main_window.py`, `app/ui/pages/page_automation.py`, `app/ui/pages/page_notifications.py`, `app/ui/pages/page_dashboard.py`
- Estilos: `app/ui/styles/styles.py`

