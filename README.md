# 🎵 ApiMusic V1 BETA

API y sistema de música para Discord basado en Python, discord.py, Wavelink, FastAPI y Lavalink.

## ✨ Características

- 🤖 Discord Music Bot
- 🎧 Lavalink 4.2.2
- 🌐 FastAPI Music API
- 🔎 Búsqueda de música
- 📋 Sistema de cola
- 🎛️ Panel interactivo
- 🔁 Repetición
- 🔀 Shuffle
- 🔊 Control de volumen
- ⏸️ Pausa y reanudación
- ▶️ Reproducción automática
- 🎵 YouTube Plugin para Lavalink

## 🧩 Arquitectura

El proyecto utiliza tres servicios independientes:

1. 🌐 Music API
2. 🤖 Discord Bot
3. 🎧 Lavalink

## 📁 Estructura

```text
ApiMusic-V1-BETA-/
├── api/
├── bot/
├── models/
├── plugins/
├── services/
├── utils/
├── data/
├── main.py
├── application.yml
├── Dockerfile.lavalink
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

## 🔐 Variables de entorno

Configura estas variables en Render. No subas `.env` a GitHub.

```text
DISCORD_TOKEN=
LAVALINK_URI=
LAVALINK_PASSWORD=
MUSIC_API_URL=
```

## ☁️ DESPLIEGUE EN RENDER

### 1. 🌐 MUSIC API

Crear un servicio Web Service desde el repositorio de GitHub.

**Runtime:** Python

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Variables necesarias:

```text
LAVALINK_URI=<URL_DE_LAVALINK>
LAVALINK_PASSWORD=<CONTRASEÑA>
```

### 2. 🤖 DISCORD BOT

Crear un servicio Background Worker desde el mismo repositorio.

**Runtime:** Python

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python -m bot.main
```

Variables necesarias:

```text
DISCORD_TOKEN=<TOKEN_DEL_BOT>
LAVALINK_URI=<URL_DE_LAVALINK>
LAVALINK_PASSWORD=<CONTRASEÑA>
MUSIC_API_URL=<URL_DE_MUSIC_API>
```

### 3. 🎧 LAVALINK

Lavalink requiere Java 17 y se ejecuta mediante el Dockerfile incluido en el proyecto.

Archivo:

```text
Dockerfile.lavalink
```

El Dockerfile prepara Java 17, descarga Lavalink 4.2.2 y copia la configuración y los plugins.

**Puerto:** 8080

Variable necesaria:

```text
LAVALINK_PASSWORD=<CONTRASEÑA>
```

## 🔗 CONEXIÓN ENTRE SERVICIOS

Una vez desplegados los servicios, configurar:

```text
Discord Bot
    │
    ├── LAVALINK_URI ──► Lavalink
    │
    └── MUSIC_API_URL ─► Music API
```

## 🧪 DESARROLLO LOCAL

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Iniciar API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Iniciar Lavalink:

```bash
java -jar Lavalink.jar
```

Iniciar Bot:

```bash
python -m bot.main
```

## 🔒 SEGURIDAD

Nunca publiques:

- Tokens de Discord
- Contraseñas de Lavalink
- Archivos `.env`
- Claves privadas

## 📌 ESTADO

**Versión:** V1 BETA

🚧 Proyecto en desarrollo.

## 👨‍💻 PROYECTO

ApiMusic V1 BETA

Repositorio GitHub:
https://github.com/Anderson-09-web/ApiMusic-V1-BETA-
