from __future__ import annotations

import locale
import os
from dataclasses import dataclass
from typing import Mapping

from .locales import SUPPORTED_LANGUAGES, match_studyn_locale


DEFAULT_LANGUAGE = "en-US"


TRANSLATIONS: Mapping[str, Mapping[str, str]] = {
    "en-US": {
        "app.title": "Studyn - Anki Sync",
        "account.fallback": "Studyn account",
        "menu.connect": "Connect account",
        "menu.sync": "Sync now",
        "menu.status": "View status",
        "menu.diagnostics": "Copy diagnostics",
        "menu.configure": "Configure server",
        "menu.language": "Language",
        "menu.update_settings": "Automatic updates",
        "menu.check_updates": "Check for updates",
        "menu.disconnect": "Disconnect",
        "onboarding.welcome": (
            "Connect this Anki profile to Studyn to sync your study statistics.\n\n"
            "1. Your browser will open.\n"
            "2. Sign in and authorize this device.\n"
            "3. Return to Anki; the first sync starts automatically.\n\n"
            "Connect now?"
        ),
        "onboarding.reconnect": (
            "This device's Studyn authorization expired or was revoked. The unusable "
            "local credential was cleared; your sync history was preserved.\n\n"
            "Reconnect now?"
        ),
        "pairing.in_progress": "A connection is already waiting for authorization in your browser.",
        "pairing.already_connected": "This profile is already connected to {display_name}.",
        "pairing.browser_opened": (
            "Your browser was opened to connect your Studyn account.\n\n"
            "Code: {code}\n\n"
            "After authorizing the device, return to Anki. You may close this window."
        ),
        "pairing.title": "Connect to Studyn",
        "pairing.connected": "Studyn account connected successfully.",
        "pairing.api_not_found": (
            "The Anki API was not found on this server.\n\n"
            "Configured server: {server}\n\n"
            "If the site is running locally, open Tools > Studyn > Configure server "
            "and enter, for example:\nhttp://127.0.0.1/api/v1/anki"
        ),
        "pairing.failed": "Could not connect to Studyn.\n\n{detail}",
        "config.title": "Studyn - Configure server",
        "config.prompt": (
            "Studyn API base URL:\n\n"
            "Production: https://studyn.org/api/v1/anki\n"
            "Local site: http://127.0.0.1/api/v1/anki"
        ),
        "config.updated": (
            "Server updated successfully.\n\n{base_url}\n\n"
            "Now open Tools > Studyn > Connect account."
        ),
        "language.title": "Studyn - Language",
        "language.prompt": (
            "Language (auto, en-US, pt-BR, or es-419):\n\n"
            "Use auto to follow the computer locale."
        ),
        "language.invalid": "Use auto, en-US, pt-BR, or es-419.",
        "language.updated": "Language saved as {language}. Restart Anki to update every menu.",
        "status.not_connected": "Not connected",
        "status.connected": "Connected to {display_name}",
        "status.never": "Never",
        "status.none": "None",
        "status.in_progress": "In progress",
        "status.idle": "Idle",
        "status.body": (
            "Anki profile: {profile_name}\nStatus: {status}\nServer: {server}\n"
            "Sync: {activity}\nLast upload: {last_sync}\nLast error: {last_error}"
        ),
        "diagnostics.copied": "Diagnostic information copied to the clipboard.",
        "diagnostics.report_title": "Studyn Anki Sync diagnostics",
        "diagnostics.generated": "Generated (UTC)",
        "diagnostics.addon_version": "Add-on version",
        "diagnostics.anki_version": "Anki version",
        "diagnostics.python_version": "Python version",
        "diagnostics.operating_system": "Operating system",
        "diagnostics.language_setting": "Language setting",
        "diagnostics.resolved_language": "Resolved language",
        "diagnostics.api_server": "API server",
        "diagnostics.automatic_sync": "Automatic sync",
        "diagnostics.update_checks": "Update checks",
        "diagnostics.connected": "Connected",
        "diagnostics.sync_state": "Sync state",
        "diagnostics.last_sync": "Last successful sync",
        "diagnostics.last_attempt": "Last sync attempt",
        "diagnostics.last_error": "Last error",
        "diagnostics.yes": "Yes",
        "diagnostics.no": "No",
        "update.title": "Studyn update available",
        "update.available": (
            "Studyn Anki Sync {latest} is available. You are using {current}.\n\n"
            "Open the download page?"
        ),
        "update.settings_title": "Studyn - Automatic updates",
        "update.enable_prompt": (
            "Automatically install future Studyn Anki Sync releases?\n\n"
            "Only packages from the official GitHub repository whose SHA-256 checksum "
            "matches the published release will be installed. Anki must be restarted "
            "after an installation."
        ),
        "update.disable_prompt": "Disable automatic Studyn Anki Sync updates?",
        "update.setting_enabled": "Automatic updates enabled.",
        "update.setting_disabled": "Automatic updates disabled.",
        "update.in_progress": "An update check or installation is already in progress.",
        "update.none": "Studyn Anki Sync is up to date.",
        "update.restart_pending": "The update is installed. Restart Anki to load it.",
        "update.check_failed": "Could not check for updates.\n\n{error}",
        "update.installed": (
            "Studyn Anki Sync {version} was installed successfully.\n\n"
            "Restart Anki to load the new version."
        ),
        "update.install_failed": "Could not install the update.\n\n{error}",
        "disconnect.not_connected": "This profile is not connected to Studyn.",
        "disconnect.confirm": "Revoke this device and disconnect the Studyn account?",
        "disconnect.failed": "Could not revoke the device. The connection was kept.\n\n{error}",
        "disconnect.done": "Device disconnected from Studyn.",
        "sync.connect_first": "Connect your Studyn account before syncing.",
        "sync.success": "Studyn synced: {days} day(s) updated.",
        "sync.collect_failed": "Could not collect the data.\n\n{message}",
        "sync.prepare_failed": "Could not prepare the sync.\n\n{message}",
        "sync.upload_failed": "Could not upload the data.\n\n{message}",
        "sync.reconnect_required": (
            "This device's Studyn authorization is no longer valid. The unusable local "
            "credential was cleared. Open Tools > Studyn > Connect account to reconnect."
        ),
        "api.https_required": "The Studyn API must use HTTPS.",
        "api.endpoint_not_found": "Endpoint not found: {url}",
        "api.connection_failed": "Could not connect to the Studyn API.",
        "api.invalid_authorization": "The API returned an invalid device authorization.",
        "api.invalid_device_token": "The API returned an invalid device token.",
        "api.code_expired": "The connection code has expired.",
        "api.error.authorization_pending": "Waiting for authorization in your browser.",
        "api.error.slow_down": "The server requested a slower polling interval.",
        "api.error.expired_token": "The connection code has expired.",
        "api.error.access_denied": "The connection request was denied.",
        "api.error.invalid_token": "The device token is invalid or has been revoked.",
        "api.error.rate_limited": "Too many requests. Please wait a moment and try again.",
        "api.error.payload_too_large": "The sync payload is too large.",
        "api.error.internal_server_error": "The Studyn server encountered an internal error.",
        "api.error.default": "Studyn API request failed (HTTP {status}).",
    },
    "pt-BR": {
        "app.title": "Studyn - Sincronização com Anki",
        "account.fallback": "conta Studyn",
        "menu.connect": "Conectar conta",
        "menu.sync": "Sincronizar agora",
        "menu.status": "Ver status",
        "menu.diagnostics": "Copiar diagnóstico",
        "menu.configure": "Configurar servidor",
        "menu.language": "Idioma",
        "menu.update_settings": "Atualizações automáticas",
        "menu.check_updates": "Verificar atualizações",
        "menu.disconnect": "Desconectar",
        "onboarding.welcome": (
            "Conecte este perfil do Anki ao Studyn para sincronizar suas estatísticas.\n\n"
            "1. O navegador será aberto.\n"
            "2. Entre na sua conta e autorize este dispositivo.\n"
            "3. Volte ao Anki; a primeira sincronização começa automaticamente.\n\n"
            "Conectar agora?"
        ),
        "onboarding.reconnect": (
            "A autorização deste dispositivo no Studyn expirou ou foi revogada. A "
            "credencial local inutilizável foi removida; seu histórico de sincronização "
            "foi preservado.\n\nReconectar agora?"
        ),
        "pairing.in_progress": "Uma conexão já está aguardando autorização no navegador.",
        "pairing.already_connected": "Este perfil já está conectado a {display_name}.",
        "pairing.browser_opened": (
            "O navegador foi aberto para conectar sua conta Studyn.\n\n"
            "Código: {code}\n\n"
            "Depois de autorizar o dispositivo, volte ao Anki. Você pode fechar esta janela."
        ),
        "pairing.title": "Conectar ao Studyn",
        "pairing.connected": "Conta Studyn conectada com sucesso.",
        "pairing.api_not_found": (
            "A API do Anki não foi encontrada neste servidor.\n\n"
            "Servidor configurado: {server}\n\n"
            "Se o site estiver rodando localmente, abra Ferramentas > Studyn > "
            "Configurar servidor e informe, por exemplo:\nhttp://127.0.0.1/api/v1/anki"
        ),
        "pairing.failed": "Não foi possível conectar ao Studyn.\n\n{detail}",
        "config.title": "Studyn - Configurar servidor",
        "config.prompt": (
            "Endereço base da API do Studyn:\n\n"
            "Produção: https://studyn.org/api/v1/anki\n"
            "Site local: http://127.0.0.1/api/v1/anki"
        ),
        "config.updated": (
            "Servidor atualizado com sucesso.\n\n{base_url}\n\n"
            "Agora abra Ferramentas > Studyn > Conectar conta."
        ),
        "language.title": "Studyn - Idioma",
        "language.prompt": (
            "Idioma (auto, en-US, pt-BR ou es-419):\n\n"
            "Use auto para seguir o idioma do computador."
        ),
        "language.invalid": "Use auto, en-US, pt-BR ou es-419.",
        "language.updated": "Idioma salvo como {language}. Reinicie o Anki para atualizar todos os menus.",
        "status.not_connected": "Não conectado",
        "status.connected": "Conectado a {display_name}",
        "status.never": "Nunca",
        "status.none": "Nenhum",
        "status.in_progress": "Em andamento",
        "status.idle": "Aguardando",
        "status.body": (
            "Perfil do Anki: {profile_name}\nStatus: {status}\nServidor: {server}\n"
            "Sincronização: {activity}\nÚltimo envio: {last_sync}\nÚltimo erro: {last_error}"
        ),
        "diagnostics.copied": "As informações de diagnóstico foram copiadas.",
        "diagnostics.report_title": "Diagnóstico do Studyn Anki Sync",
        "diagnostics.generated": "Gerado (UTC)",
        "diagnostics.addon_version": "Versão do add-on",
        "diagnostics.anki_version": "Versão do Anki",
        "diagnostics.python_version": "Versão do Python",
        "diagnostics.operating_system": "Sistema operacional",
        "diagnostics.language_setting": "Configuração de idioma",
        "diagnostics.resolved_language": "Idioma utilizado",
        "diagnostics.api_server": "Servidor da API",
        "diagnostics.automatic_sync": "Sincronização automática",
        "diagnostics.update_checks": "Verificação de atualizações",
        "diagnostics.connected": "Conectado",
        "diagnostics.sync_state": "Estado da sincronização",
        "diagnostics.last_sync": "Última sincronização concluída",
        "diagnostics.last_attempt": "Última tentativa de sincronização",
        "diagnostics.last_error": "Último erro",
        "diagnostics.yes": "Sim",
        "diagnostics.no": "Não",
        "update.title": "Atualização do Studyn disponível",
        "update.available": (
            "O Studyn Anki Sync {latest} está disponível. Você está usando "
            "a versão {current}.\n\nAbrir a página de download?"
        ),
        "update.settings_title": "Studyn - Atualizações automáticas",
        "update.enable_prompt": (
            "Instalar automaticamente as próximas versões do Studyn Anki Sync?\n\n"
            "Somente pacotes do repositório oficial no GitHub cujo checksum SHA-256 "
            "corresponda ao publicado na release serão instalados. O Anki precisará ser "
            "reiniciado após uma instalação."
        ),
        "update.disable_prompt": "Desativar as atualizações automáticas do Studyn Anki Sync?",
        "update.setting_enabled": "Atualizações automáticas ativadas.",
        "update.setting_disabled": "Atualizações automáticas desativadas.",
        "update.in_progress": "Uma verificação ou instalação de atualização já está em andamento.",
        "update.none": "O Studyn Anki Sync está atualizado.",
        "update.restart_pending": "A atualização está instalada. Reinicie o Anki para carregá-la.",
        "update.check_failed": "Não foi possível verificar atualizações.\n\n{error}",
        "update.installed": (
            "O Studyn Anki Sync {version} foi instalado com sucesso.\n\n"
            "Reinicie o Anki para carregar a nova versão."
        ),
        "update.install_failed": "Não foi possível instalar a atualização.\n\n{error}",
        "disconnect.not_connected": "Este perfil não está conectado ao Studyn.",
        "disconnect.confirm": "Revogar este dispositivo e desconectar a conta Studyn?",
        "disconnect.failed": "Não foi possível revogar o dispositivo. A conexão foi mantida.\n\n{error}",
        "disconnect.done": "Dispositivo desconectado do Studyn.",
        "sync.connect_first": "Conecte sua conta Studyn antes de sincronizar.",
        "sync.success": "Studyn sincronizado: {days} dia(s) atualizado(s).",
        "sync.collect_failed": "Não foi possível coletar os dados.\n\n{message}",
        "sync.prepare_failed": "Não foi possível preparar a sincronização.\n\n{message}",
        "sync.upload_failed": "Não foi possível enviar os dados.\n\n{message}",
        "sync.reconnect_required": (
            "A autorização deste dispositivo no Studyn não é mais válida. A credencial "
            "local inutilizável foi removida. Abra Ferramentas > Studyn > Conectar conta "
            "para conectar novamente."
        ),
        "api.https_required": "A API do Studyn deve usar HTTPS.",
        "api.endpoint_not_found": "Endpoint não encontrado: {url}",
        "api.connection_failed": "Não foi possível conectar à API do Studyn.",
        "api.invalid_authorization": "A API retornou uma autorização de dispositivo inválida.",
        "api.invalid_device_token": "A API retornou um token de dispositivo inválido.",
        "api.code_expired": "O código de conexão expirou.",
        "api.error.authorization_pending": "Aguardando autorização no navegador.",
        "api.error.slow_down": "O servidor solicitou um intervalo maior entre as tentativas.",
        "api.error.expired_token": "O código de conexão expirou.",
        "api.error.access_denied": "A solicitação de conexão foi negada.",
        "api.error.invalid_token": "O token do dispositivo é inválido ou foi revogado.",
        "api.error.rate_limited": "Muitas solicitações. Aguarde um momento e tente novamente.",
        "api.error.payload_too_large": "Os dados da sincronização são muito grandes.",
        "api.error.internal_server_error": "O servidor do Studyn encontrou um erro interno.",
        "api.error.default": "A solicitação à API do Studyn falhou (HTTP {status}).",
    },
    "es-419": {
        "app.title": "Studyn - Sincronización con Anki",
        "account.fallback": "cuenta de Studyn",
        "menu.connect": "Conectar cuenta",
        "menu.sync": "Sincronizar ahora",
        "menu.status": "Ver estado",
        "menu.diagnostics": "Copiar diagnóstico",
        "menu.configure": "Configurar servidor",
        "menu.language": "Idioma",
        "menu.update_settings": "Actualizaciones automáticas",
        "menu.check_updates": "Buscar actualizaciones",
        "menu.disconnect": "Desconectar",
        "onboarding.welcome": (
            "Conecta este perfil de Anki con Studyn para sincronizar tus estadísticas.\n\n"
            "1. Se abrirá el navegador.\n"
            "2. Inicia sesión y autoriza este dispositivo.\n"
            "3. Vuelve a Anki; la primera sincronización comenzará automáticamente.\n\n"
            "¿Conectar ahora?"
        ),
        "onboarding.reconnect": (
            "La autorización de este dispositivo en Studyn venció o fue revocada. Se "
            "eliminó la credencial local inutilizable; se conservó tu historial de "
            "sincronización.\n\n¿Volver a conectar ahora?"
        ),
        "pairing.in_progress": "Ya hay una conexión esperando autorización en el navegador.",
        "pairing.already_connected": "Este perfil ya está conectado a {display_name}.",
        "pairing.browser_opened": (
            "Se abrió el navegador para conectar tu cuenta de Studyn.\n\n"
            "Código: {code}\n\n"
            "Después de autorizar el dispositivo, vuelve a Anki. Puedes cerrar esta ventana."
        ),
        "pairing.title": "Conectar con Studyn",
        "pairing.connected": "La cuenta de Studyn se conectó correctamente.",
        "pairing.api_not_found": (
            "No se encontró la API de Anki en este servidor.\n\n"
            "Servidor configurado: {server}\n\n"
            "Si el sitio se ejecuta localmente, abre Herramientas > Studyn > "
            "Configurar servidor e ingresa, por ejemplo:\nhttp://127.0.0.1/api/v1/anki"
        ),
        "pairing.failed": "No se pudo conectar con Studyn.\n\n{detail}",
        "config.title": "Studyn - Configurar servidor",
        "config.prompt": (
            "URL base de la API de Studyn:\n\n"
            "Producción: https://studyn.org/api/v1/anki\n"
            "Sitio local: http://127.0.0.1/api/v1/anki"
        ),
        "config.updated": (
            "El servidor se actualizó correctamente.\n\n{base_url}\n\n"
            "Ahora abre Herramientas > Studyn > Conectar cuenta."
        ),
        "language.title": "Studyn - Idioma",
        "language.prompt": (
            "Idioma (auto, en-US, pt-BR o es-419):\n\n"
            "Usa auto para seguir el idioma de la computadora."
        ),
        "language.invalid": "Usa auto, en-US, pt-BR o es-419.",
        "language.updated": "Idioma guardado como {language}. Reinicia Anki para actualizar todos los menús.",
        "status.not_connected": "Sin conexión",
        "status.connected": "Conectado a {display_name}",
        "status.never": "Nunca",
        "status.none": "Ninguno",
        "status.in_progress": "En curso",
        "status.idle": "En espera",
        "status.body": (
            "Perfil de Anki: {profile_name}\nEstado: {status}\nServidor: {server}\n"
            "Sincronización: {activity}\nÚltimo envío: {last_sync}\nÚltimo error: {last_error}"
        ),
        "diagnostics.copied": "La información de diagnóstico se copió al portapapeles.",
        "diagnostics.report_title": "Diagnóstico de Studyn Anki Sync",
        "diagnostics.generated": "Generado (UTC)",
        "diagnostics.addon_version": "Versión del complemento",
        "diagnostics.anki_version": "Versión de Anki",
        "diagnostics.python_version": "Versión de Python",
        "diagnostics.operating_system": "Sistema operativo",
        "diagnostics.language_setting": "Configuración de idioma",
        "diagnostics.resolved_language": "Idioma utilizado",
        "diagnostics.api_server": "Servidor de la API",
        "diagnostics.automatic_sync": "Sincronización automática",
        "diagnostics.update_checks": "Búsqueda de actualizaciones",
        "diagnostics.connected": "Conectado",
        "diagnostics.sync_state": "Estado de sincronización",
        "diagnostics.last_sync": "Última sincronización completada",
        "diagnostics.last_attempt": "Último intento de sincronización",
        "diagnostics.last_error": "Último error",
        "diagnostics.yes": "Sí",
        "diagnostics.no": "No",
        "update.title": "Actualización de Studyn disponible",
        "update.available": (
            "Studyn Anki Sync {latest} está disponible. Estás usando la versión "
            "{current}.\n\n¿Abrir la página de descarga?"
        ),
        "update.settings_title": "Studyn - Actualizaciones automáticas",
        "update.enable_prompt": (
            "¿Instalar automáticamente las próximas versiones de Studyn Anki Sync?\n\n"
            "Solo se instalarán paquetes del repositorio oficial de GitHub cuyo checksum "
            "SHA-256 coincida con el publicado en el lanzamiento. Se deberá reiniciar Anki "
            "después de una instalación."
        ),
        "update.disable_prompt": "¿Desactivar las actualizaciones automáticas de Studyn Anki Sync?",
        "update.setting_enabled": "Actualizaciones automáticas activadas.",
        "update.setting_disabled": "Actualizaciones automáticas desactivadas.",
        "update.in_progress": "Ya hay una búsqueda o instalación de actualización en curso.",
        "update.none": "Studyn Anki Sync está actualizado.",
        "update.restart_pending": "La actualización está instalada. Reinicia Anki para cargarla.",
        "update.check_failed": "No se pudieron buscar actualizaciones.\n\n{error}",
        "update.installed": (
            "Studyn Anki Sync {version} se instaló correctamente.\n\n"
            "Reinicia Anki para cargar la nueva versión."
        ),
        "update.install_failed": "No se pudo instalar la actualización.\n\n{error}",
        "disconnect.not_connected": "Este perfil no está conectado a Studyn.",
        "disconnect.confirm": "¿Revocar este dispositivo y desconectar la cuenta de Studyn?",
        "disconnect.failed": "No se pudo revocar el dispositivo. Se mantuvo la conexión.\n\n{error}",
        "disconnect.done": "Dispositivo desconectado de Studyn.",
        "sync.connect_first": "Conecta tu cuenta de Studyn antes de sincronizar.",
        "sync.success": "Studyn sincronizado: {days} día(s) actualizado(s).",
        "sync.collect_failed": "No se pudieron recopilar los datos.\n\n{message}",
        "sync.prepare_failed": "No se pudo preparar la sincronización.\n\n{message}",
        "sync.upload_failed": "No se pudieron enviar los datos.\n\n{message}",
        "sync.reconnect_required": (
            "La autorización de este dispositivo en Studyn ya no es válida. Se eliminó "
            "la credencial local inutilizable. Abre Herramientas > Studyn > Conectar "
            "cuenta para volver a conectarlo."
        ),
        "api.https_required": "La API de Studyn debe usar HTTPS.",
        "api.endpoint_not_found": "No se encontró el endpoint: {url}",
        "api.connection_failed": "No se pudo conectar con la API de Studyn.",
        "api.invalid_authorization": "La API devolvió una autorización de dispositivo no válida.",
        "api.invalid_device_token": "La API devolvió un token de dispositivo no válido.",
        "api.code_expired": "El código de conexión venció.",
        "api.error.authorization_pending": "Esperando autorización en el navegador.",
        "api.error.slow_down": "El servidor solicitó un intervalo mayor entre intentos.",
        "api.error.expired_token": "El código de conexión venció.",
        "api.error.access_denied": "Se rechazó la solicitud de conexión.",
        "api.error.invalid_token": "El token del dispositivo no es válido o fue revocado.",
        "api.error.rate_limited": "Demasiadas solicitudes. Espera un momento e inténtalo de nuevo.",
        "api.error.payload_too_large": "Los datos de sincronización son demasiado grandes.",
        "api.error.internal_server_error": "El servidor de Studyn encontró un error interno.",
        "api.error.default": "La solicitud a la API de Studyn falló (HTTP {status}).",
    },
}


def normalize_configured_language(value: object) -> str:
    raw = str(value or "auto").strip().lower().replace("_", "-")
    if raw in {"auto", "system", "default"}:
        return "auto"
    return match_studyn_locale(raw) or "auto"


def resolve_language(configured: object = "auto", system_locale: str | None = None) -> str:
    normalized = normalize_configured_language(configured)
    if normalized != "auto":
        return normalized
    return _language_from_locale(system_locale or _system_locale_name())


def _language_from_locale(value: object) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    matched = match_studyn_locale(raw)
    if matched:
        return matched
    if "portuguese" in raw:
        return "pt-BR"
    if "spanish" in raw:
        return "es-419"
    if "english" in raw:
        return "en-US"
    return DEFAULT_LANGUAGE


def _system_locale_name() -> str:
    try:
        from aqt.qt import QLocale

        name = str(QLocale.system().name() or "")
        if name:
            return name
    except (ImportError, AttributeError, RuntimeError):
        pass

    try:
        name = locale.getlocale()[0]
        if name:
            return str(name)
    except (TypeError, ValueError):
        pass

    return os.environ.get("LC_ALL") or os.environ.get("LANG") or ""


@dataclass(frozen=True)
class Translator:
    language: str

    @classmethod
    def create(
        cls, configured: object = "auto", system_locale: str | None = None
    ) -> "Translator":
        return cls(resolve_language(configured, system_locale))

    def t(self, key: str, **values: object) -> str:
        catalog = TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE])
        template = catalog.get(key) or TRANSLATIONS[DEFAULT_LANGUAGE].get(key) or key
        return template.format(**values)
