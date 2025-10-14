# Catálogo de comandos QC1

Esta tabla resume los comandos expuestos en `app/comm/registry.py`. Cada comando se construye con la cabecera `QC1,<MODEL>,<DEV>,<SEQ>,<TS>,<CMD>` y admite los campos que se listan a continuación. Usa `SerialCommandService` para automatizar secuencia y checksum.

| Nombre | Categoría | Posicionales | Campos clave | Requiere PWD | Descripción breve |
| --- | --- | --- | --- | --- | --- |
| SYS.INFO? | system | — | — | No | Solicita información general del equipo |
| SYS.REBOOT | system | — | DELAY | Sí | Programa un reinicio controlado |
| SEC.PWD.SET | security | OLD, NEW | — | No | Cambia la contraseña de programación |
| CONTACT.AUTH.SET | contacts | — | LIST | Sí | Sincroniza números autorizados |
| CONTACT.AUTH.GET? | contacts | — | — | No | Consulta los números autorizados |
| CONTACT.GROUP.SET | contacts | GROUP | NAME, CHANNEL, MEMBERS | Sí | Define o actualiza un grupo individual |
| CONTACT.GROUP.BULK | contacts | — | LIST | Sí | Reemplaza la tabla de grupos usando JSON |
| CONTACT.GROUP.TEST | contacts | GROUP | TEMPLATE | Sí | Envía un mensaje de prueba al grupo |
| IO.INPUT.MAP | automation | — | MAP | Sí | Mapea entradas a eventos |
| IO.OUTPUT.MAP | automation | — | MAP | Sí | Configura salidas y modos |
| IO.SCHEDULE.SET | automation | — | LIST | Sí | Crea horarios operativos |
| IO.OUTPUT.TRIGGER | automation | OUTPUT | ACTION | Sí | Fuerza una salida específica |
| AUDIO.SLOTS? | audio | — | — | No | Lista slots de audio |
| AUDIO.PLAY | audio | SLOT, ACTION | DUR, LOOP | Sí | Activa/ detiene reproducción |
| AUDIO.UPLOAD | audio | SLOT, SIZE | FORMAT, SHA1, ENC | Sí | Inicia carga de audio |
| SRV.MQTT.SET | server | — | HOST, PORT, USER, PASS, TOPIC_UP, TOPIC_DOWN, TLS | Sí | Configura el broker MQTT |
| SRV.MQTT.TEST | server | — | — | No | Pide un ping al broker |
| NTF.CHANNEL.SET | notifications | — | WHATSAPP, APP, SMS, EMAIL, VOICE | Sí | Activa/desactiva canales |
| NTF.TEMPLATE.SET | notifications | NAME | BODY | Sí | Guarda una plantilla |
| LOGS.PULL? | logs | — | LINES | No | Recupera registros circulares |

Cada comando se describe con `CommandSpec` y puede consultarse a través de `get_command("CMD")`.
