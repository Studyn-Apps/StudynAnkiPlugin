<div align="center">
  <img src="static/logo.png" width="128" alt="Logo de Studyn">
  <h1>Studyn Anki Sync</h1>
  <p>Convierte tu actividad de estudio en Anki en progreso dentro de la clasificación global de Studyn.</p>

  <p>
    <a href="https://github.com/Studyn-Apps/StudynAnkiPlugin/releases"><img src="https://img.shields.io/github/v/release/Studyn-Apps/StudynAnkiPlugin?style=flat-square" alt="Versión más reciente"></a>
    <a href="https://github.com/Studyn-Apps/StudynAnkiPlugin/actions/workflows/release.yml"><img src="https://img.shields.io/github/actions/workflow/status/Studyn-Apps/StudynAnkiPlugin/release.yml?style=flat-square&label=release" alt="Automatización de versiones"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/Studyn-Apps/StudynAnkiPlugin?style=flat-square" alt="Licencia MIT"></a>
  </p>

  <p>
    <a href="README.md">English</a> ·
    <a href="README.pt-BR.md">Português (Brasil)</a> ·
    <strong>Español (Latinoamérica)</strong>
  </p>
</div>

Studyn Anki Sync es el complemento oficial y de código abierto que conecta Anki
Desktop con [Studyn](https://studyn.org/anki). Envía de forma segura estadísticas
agregadas de tus repasos para que puedas seguir tu constancia, comparar tu
progreso y participar en la clasificación global sin exponer el contenido de
tus tarjetas.

## Características principales

- **Clasificación global:** tu actividad en Anki contribuye a tu perfil de Studyn.
- **Sincronización automática:** los repasos se envían en segundo plano después
  de estudiar.
- **Totales confiables:** las instantáneas autoritativas evitan estadísticas
  duplicadas y reflejan correctamente los repasos deshechos.
- **Métricas útiles:** repasos, tiempo de estudio, respuestas Otra vez/Difícil/Bien/Fácil,
  totales históricos y racha actual.
- **Compatible con perfiles:** cada perfil de Anki puede conectarse con su propia
  cuenta de Studyn.
- **Traducido:** compatibilidad automática con `es-419`, `en-US` y `pt-BR`.
- **Soporte sencillo:** copia un diagnóstico sanitizado directamente desde Anki.
- **Avisos de actualización:** recibe una notificación cuando exista una nueva versión oficial.
- **Ligero:** no requiere dependencias externas de Python durante la ejecución.

## Privacidad desde el diseño

Solo se envían a Studyn estadísticas agregadas de estudio. El complemento
**nunca envía**:

- textos, preguntas o respuestas de las tarjetas;
- nombres de mazos, etiquetas, IDs de tarjetas o IDs de notas;
- tu usuario o contraseña de AnkiWeb;
- la base de datos de tu colección ni archivos multimedia.

El token de autorización se guarda localmente en
`user_files/credentials.json` y está separado por perfil de Anki. Puedes
revocarlo en cualquier momento desde **Herramientas > Studyn > Desconectar**.

Informa los problemas de seguridad en privado según [SECURITY.md](SECURITY.md).

## Requisitos

- Anki Desktop 2.1.50 o posterior;
- una cuenta de Studyn;
- conexión a internet para vincular la cuenta y sincronizar.

El complemento funciona en Anki Desktop. Los repasos realizados en AnkiMobile,
AnkiDroid u otro cliente se incluirán después de que ese historial llegue a Anki
Desktop y el complemento se sincronice.

## Instalación

1. Descarga el archivo `.ankiaddon` más reciente desde
   [GitHub Releases](https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/latest)
   o desde la [página de Anki en Studyn](https://studyn.org/anki).
2. Abre el archivo descargado con Anki Desktop y confirma la instalación.
3. Reinicia Anki.
4. Abre **Herramientas > Studyn > Conectar cuenta**.
5. Autoriza la conexión en la ventana del navegador que se abrirá.

Studyn realiza la primera sincronización en cuanto se conecta la cuenta. Para
actualizar el complemento posteriormente, instala el nuevo `.ankiaddon` sobre
la versión existente; tu autorización local se conservará.

## Uso

El menú **Herramientas > Studyn** incluye todas las acciones del complemento:

| Acción | Función |
| --- | --- |
| **Conectar cuenta** | Vincula el perfil actual de Anki con Studyn. |
| **Sincronizar ahora** | Envía inmediatamente las estadísticas agregadas más recientes. |
| **Ver estado** | Muestra la cuenta, el servidor, la última sincronización y el último error. |
| **Copiar diagnóstico** | Copia información técnica sanitizada para solicitudes de soporte. |
| **Configurar servidor** | Cambia la dirección de la API, principalmente para desarrollo local. |
| **Idioma** | Selecciona la detección automática o un idioma compatible. |
| **Desconectar** | Revoca el dispositivo y elimina su autorización local. |

### Idiomas

De forma predeterminada, la interfaz sigue el idioma de la computadora:

- las configuraciones regionales en español usan `es-419`;
- las de portugués de Brasil usan `pt-BR`;
- el inglés y los idiomas sin traducción usan `en-US`.

Para elegirlo manualmente, abre **Herramientas > Studyn > Idioma**, ingresa
`auto`, `es-419`, `en-US` o `pt-BR` y reinicia Anki para actualizar todos los
elementos del menú.

## Cómo funciona la sincronización

La primera conexión envía los 365 días de estudio anteriores. Las
sincronizaciones habituales vuelven a enviar los 31 días más recientes y
amplían automáticamente el periodo de recuperación después de mucho tiempo sin
conexión. Cada solicitud contiene totales absolutos para un intervalo de fechas,
por lo que repetirla no suma los mismos repasos dos veces.

Estos intervalos y límites pueden ajustarse en `config.json`. Consulta
[config.md](config.md) para conocer todas las opciones y
[docs/API_CONTRACT.md](docs/API_CONTRACT.md) para revisar el protocolo del backend.

De forma predeterminada, el complemento consulta la API oficial de GitHub
Releases como máximo una vez cada 24 horas. No envía credenciales de Studyn en
esta solicitud y muestra una sola notificación por versión. Configura
`check_for_updates` como `false` para desactivarla o cambia
`update_check_interval_hours` para ajustar el intervalo.

## Solución de problemas

**El navegador muestra `Not Found` al conectar.**

Abre **Herramientas > Studyn > Configurar servidor** y confirma que la dirección
apunte a la base de la API e incluya `/api/v1/anki`. Para desarrollo local, usa
`http://127.0.0.1:3000/api/v1/anki` cuando el sitio se ejecute en el puerto 3000.

**La clasificación todavía no se actualiza.**

Abre **Herramientas > Studyn > Ver estado** para revisar la última sincronización y
luego selecciona **Sincronizar ahora**. Si los repasos provienen de otro cliente
de Anki, primero sincroniza ese cliente con Anki Desktop.

**La interfaz aparece en el idioma incorrecto.**

Elige el idioma en **Herramientas > Studyn > Idioma** y reinicia Anki.

Para solicitar soporte, usa **Herramientas > Studyn > Copiar diagnóstico** y
revisa el texto antes de compartirlo. Los tokens, IDs de dispositivos,
identidades de perfiles, contenido de tarjetas y credenciales en URLs se
excluyen o redactan.

## Desarrollo

El proyecto usa solamente la biblioteca estándar de Python durante su ejecución.
Con Python 3 instalado, ejecuta las pruebas y genera el paquete con:

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

El archivo instalable se genera en `dist/`. Para probar sin utilizar la API de
producción, inicia el servidor simulado incluido:

```powershell
python tools/mock_api.py
```

Luego configura **Herramientas > Studyn > Configurar servidor** con:

```text
http://127.0.0.1:8765/api/v1/anki
```

Las contribuciones son bienvenidas. Lee [CONTRIBUTING.md](CONTRIBUTING.md) antes
de abrir un pull request, consulta [CHANGELOG.md](CHANGELOG.md) para revisar el
historial y sigue [SECURITY.md](SECURITY.md) para informar vulnerabilidades en privado.

## Versiones

Las etiquetas que coinciden con la versión del complemento activan la
automatización de publicación. Por ejemplo, al enviar `v0.3.1`, GitHub ejecuta
las pruebas, genera el `.ankiaddon` y su checksum SHA-256 y publica ambos archivos en Releases. La lista completa
para mantenedores está en [CONTRIBUTING.md](CONTRIBUTING.md#releases).

## Licencia

Publicado bajo la [Licencia MIT](LICENSE).
