from __future__ import annotations

from typing import Dict

from .models import CommandField, CommandSpec


COMMANDS: Dict[str, CommandSpec] = {
    # --- Sistema / seguridad -------------------------------------------------
    "SYS.INFO?": CommandSpec(
        name="SYS.INFO?",
        description="Consulta status general del equipo (modelo, firmware, estado).",
        category="system",
        positional=(),
        keyword=(),
        requires_password=False,
    ),
    "SYS.REBOOT": CommandSpec(
        name="SYS.REBOOT",
        description="Solicita reinicio controlado del equipo.",
        category="system",
        positional=(),
        keyword=(
            CommandField("DELAY", "Segundos antes de reiniciar", required=False, default="5"),
        ),
        requires_password=True,
    ),
    "SEC.PWD.SET": CommandSpec(
        name="SEC.PWD.SET",
        description="Actualiza la contraseña de programación.",
        category="security",
        positional=(
            CommandField("OLD", "Contraseña actual"),
            CommandField("NEW", "Nueva contraseña"),
        ),
        keyword=(),
        requires_password=False,
    ),
    # --- Contactos -----------------------------------------------------------
    "CONTACT.AUTH.SET": CommandSpec(
        name="CONTACT.AUTH.SET",
        description="Carga números autorizados (E164 separados por punto y coma).",
        category="contacts",
        positional=(),
        keyword=(
            CommandField("LIST", "Números E164 separados por ';'"),
        ),
        requires_password=True,
    ),
    "CONTACT.AUTH.GET?": CommandSpec(
        name="CONTACT.AUTH.GET?",
        description="Solicita lista de números autorizados.",
        category="contacts",
        positional=(),
        keyword=(),
        requires_password=False,
    ),
    "CONTACT.GROUP.SET": CommandSpec(
        name="CONTACT.GROUP.SET",
        description="Configura un grupo individual de difusión.",
        category="contacts",
        positional=(
            CommandField("GROUP", "Identificador de grupo"),
        ),
        keyword=(
            CommandField("NAME", "Nombre legible"),
            CommandField("CHANNEL", "Tipo de canal: WA|APP|SMS", required=False, default="WA"),
            CommandField("MEMBERS", "Lista CSV de números o IDs"),
        ),
        requires_password=True,
    ),
    "CONTACT.GROUP.BULK": CommandSpec(
        name="CONTACT.GROUP.BULK",
        description="Sincroniza todos los grupos en formato JSON.",
        category="contacts",
        positional=(),
        keyword=(
            CommandField("LIST", "Lista JSON de grupos"),
        ),
        requires_password=True,
    ),
    "CONTACT.GROUP.TEST": CommandSpec(
        name="CONTACT.GROUP.TEST",
        description="Dispara un mensaje de prueba al grupo indicado.",
        category="contacts",
        positional=(
            CommandField("GROUP", "Identificador de grupo"),
        ),
        keyword=(
            CommandField("TEMPLATE", "Nombre de plantilla a usar", required=False, default="prueba"),
        ),
        requires_password=True,
    ),
    # --- Automatización ------------------------------------------------------
    "IO.INPUT.MAP": CommandSpec(
        name="IO.INPUT.MAP",
        description="Asocia entradas digitales a eventos (JSON compacto).",
        category="automation",
        positional=(),
        keyword=(
            CommandField("MAP", "JSON con definición de entradas"),
        ),
        requires_password=True,
    ),
    "IO.OUTPUT.MAP": CommandSpec(
        name="IO.OUTPUT.MAP",
        description="Configura salidas, tiempos y modos.",
        category="automation",
        positional=(),
        keyword=(
            CommandField("MAP", "JSON con definición de salidas"),
        ),
        requires_password=True,
    ),
    "IO.SCHEDULE.SET": CommandSpec(
        name="IO.SCHEDULE.SET",
        description="Programa horarios operativos.",
        category="automation",
        positional=(),
        keyword=(
            CommandField("LIST", "JSON con arreglo de horarios"),
        ),
        requires_password=True,
    ),
    "IO.OUTPUT.TRIGGER": CommandSpec(
        name="IO.OUTPUT.TRIGGER",
        description="Activa o libera una salida concreta.",
        category="automation",
        positional=(
            CommandField("OUTPUT", "Nombre de salida"),
        ),
        keyword=(
            CommandField("ACTION", "ACCION: ACTIVAR|LIBERAR"),
        ),
        requires_password=True,
    ),
    # --- Audio ----------------------------------------------------------------
    "AUDIO.SLOTS?": CommandSpec(
        name="AUDIO.SLOTS?",
        description="Consulta inventario de audios disponibles.",
        category="audio",
        positional=(),
        keyword=(),
        requires_password=False,
    ),
    "AUDIO.PLAY": CommandSpec(
        name="AUDIO.PLAY",
        description="Activa/desactiva reproducción en un slot.",
        category="audio",
        positional=(
            CommandField("SLOT", "Número de slot"),
            CommandField("ACTION", "ON u OFF"),
        ),
        keyword=(
            CommandField("DUR", "Duración en segundos", required=False),
            CommandField("LOOP", "1 para repetir", required=False),
        ),
        requires_password=True,
    ),
    "AUDIO.UPLOAD": CommandSpec(
        name="AUDIO.UPLOAD",
        description="Inicia carga chunked de audio (usar QC1BlobSession).",
        category="audio",
        positional=(
            CommandField("SLOT", "Slot destino"),
            CommandField("SIZE", "Tamaño en bytes"),
        ),
        keyword=(
            CommandField("FORMAT", "Formato WAV|MP3"),
            CommandField("SHA1", "Checksum opcional", required=False),
            CommandField("ENC", "1 si se debe cifrar", required=False),
        ),
        requires_password=True,
    ),
    # --- Servidor -------------------------------------------------------------
    "SRV.MQTT.SET": CommandSpec(
        name="SRV.MQTT.SET",
        description="Configura parámetros MQTT (broker Linseg).",
        category="server",
        positional=(),
        keyword=(
            CommandField("HOST", "Hostname o IP"),
            CommandField("PORT", "Puerto"),
            CommandField("USER", "Usuario"),
            CommandField("PASS", "Contraseña"),
            CommandField("TOPIC_UP", "Topic publicación"),
            CommandField("TOPIC_DOWN", "Topic suscripción"),
            CommandField("TLS", "0/1 para TLS", required=False, default="0"),
        ),
        requires_password=True,
    ),
    "SRV.MQTT.TEST": CommandSpec(
        name="SRV.MQTT.TEST",
        description="Solicita ping al broker configurado.",
        category="server",
        positional=(),
        keyword=(),
        requires_password=False,
    ),
    # --- Notificaciones ------------------------------------------------------
    "NTF.CHANNEL.SET": CommandSpec(
        name="NTF.CHANNEL.SET",
        description="Activa/desactiva canales de notificación.",
        category="notifications",
        positional=(),
        keyword=(
            CommandField("WHATSAPP", "0/1"),
            CommandField("APP", "0/1"),
            CommandField("SMS", "0/1", required=False, default="0"),
            CommandField("EMAIL", "0/1", required=False, default="0"),
            CommandField("VOICE", "0/1", required=False, default="0"),
        ),
        requires_password=True,
    ),
    "NTF.TEMPLATE.SET": CommandSpec(
        name="NTF.TEMPLATE.SET",
        description="Guarda plantilla de mensaje por evento.",
        category="notifications",
        positional=(
            CommandField("NAME", "Nombre de plantilla"),
        ),
        keyword=(
            CommandField("BODY", "Contenido con placeholders"),
        ),
        requires_password=True,
    ),
    # --- Logs ----------------------------------------------------------------
    "LOGS.PULL?": CommandSpec(
        name="LOGS.PULL?",
        description="Solicita lote de logs circulares.",
        category="logs",
        positional=(),
        keyword=(
            CommandField("LINES", "Máximo de líneas", required=False, default="100"),
        ),
        requires_password=False,
    ),
}


def get_command(name: str) -> CommandSpec:
    try:
        return COMMANDS[name]
    except KeyError as exc:
        raise KeyError(f"Comando no registrado: {name}") from exc


__all__ = ["COMMANDS", "get_command"]
