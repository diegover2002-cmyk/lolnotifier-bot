po# 🚀 Instrucciones SÚPER FÁCILES: Instala LoLNotifierBot (5-10 minutos)

**Para Windows 11, sin experiencia técnica. ¡Copiar y pegar todo!**

## ✅ Requisitos (verifica primero)

1. **Docker Desktop abierto y VERDE** (icono en barra tareas).
   - Si está ROJO: Cierra Docker > Abre de nuevo > Espera verde.
   ![Docker Verde](docker_verde.png) *(Toma screenshot de tu barra tareas con Docker verde)*

2. **Tokens listos:**
   - **TELEGRAM_TOKEN**: Habla con [@BotFather](https://t.me/botfather) en Telegram → `/newbot` → Copia el token largo (ej: `123456:ABCdef...`).
   - **RIOT_API_KEY**: Ve a [developer.riotgames.com](https://developer.riotgames.com/) → Login gratis → Crea app → Copia tu key (ej: `RGAPI-xxxxxxxxxx`).

**¡Si no tienes tokens, obténlos AHORA! (2 min)**

---

## 📋 Pasos (copia-pega exacto)

### **Paso 1: Abre la carpeta**

- Abre **Explorador de Archivos** (Win + E).
- Ve a: `C:\Users\diego\bot telegram lol\lolnotifier`
- **Screenshot aquí**: Carpeta lolnotifier abierta.
![Carpeta lolnotifier](carpeta_lolnotifier.png)

### **Paso 2: Crea archivo .env (¡IMPORTANTE!)**

1. **Clic derecho** en espacio vacío de la carpeta → **Nuevo** → **Documento de texto**.
2. **Renombra** a `.env` (confirma cambio de extensión).
3. **Abre con Notepad** (doble clic).
4. **BORRA todo** y pega ÉSTO (cambia TU_token y TU_key):

```
TELEGRAM_TOKEN=TU_TOKEN_AQUI
RIOT_API_KEY=TU_RIOT_KEY_AQUI
```

1. **Guardar** (Ctrl + S) → **Cierra Notepad**.

- **Screenshot aquí**: .env abierto en Notepad con tokens.
![.env Editado](env_editado.png)

**¡Error común: Tokens vacíos o mal pegados! Verifica doble.**

### **Paso 3: Abre Terminal en la carpeta**

1. En la carpeta lolnotifier: **Shift + Clic derecho** → **Abrir PowerShell/CMD aquí** (o usa VSCode Terminal).
2. Escribe y **Enter**:

   ```
   docker-compose up -d
   ```

- Espera "done" (1-2 min primera vez).
- **Screenshot aquí**: Terminal con "done".
![Docker Up](docker_up.png)

**¡Error común: "No docker-compose"? Docker no está verde → Reinicia Docker!**

### **Paso 4: ¡Prueba el Bot!**

1. Telegram → Busca **@TuBot** (nombre de BotFather).
2. Envía: `/start`
3. **Personal**: `/set_lol_summoner TuNick la2`
4. **Pro como Faker**: `/add_pro Faker kr`

- **¡Listo!** Recibirás notificaciones de partidas.
- **Screenshot aquí**: Chat Telegram con /start.
![Bot Telegram](bot_telegram.png)

---

## ❌ Errores Comunes & Fixes Rápidos

| Error | Fix |
|-------|-----|
| **Docker rojo** | Reinicia Docker Desktop. |
| **"No such file .env"** | Crea .env Paso 2. |
| **Tokens no funcionan** | Copia/pega NUEVO token/key. |
| **Bot no responde** | `docker-compose down` + `up -d` otra vez. |
| **"Permission denied"** | Ejecuta Terminal **como Admin**. |

## 🎉 ¡Éxito

- Bot corriendo 24/7 (reinicia auto).
- Para parar: Terminal → `docker-compose down`
- Actualizar: `docker-compose pull && up -d`

**Tiempo total: 5-10 min. ¡Notifs de Faker y tuyos! GLHF ⚔️**

*(Imágenes: Toma screenshots en cada paso y reemplaza placeholders para tu guía personal.)*
