# AI Agent Review Skill for LoLNotifierBot

## Propósito
Este archivo sirve como guía para agentes AI que revisan la calidad, lógica y documentación del repositorio LoLNotifierBot.

## Checklist de revisión automática

### 1. Lógica y arquitectura
- ¿La lógica principal del bot es clara y modular?
- ¿Se separan correctamente las responsabilidades (API, DB, handlers, polling, logging)?
- ¿El flujo de notificaciones es robusto ante errores?

### 2. Documentación
- ¿Existe README.md actualizado y claro?
- ¿Hay instrucciones de usuario (instrucciones_usuario.md) comprensibles?
- ¿Se mantiene un CHANGELOG o TODO actualizado?

### 3. Seguridad y configuración
- ¿Los secretos (tokens, API keys) están fuera del repo?
- ¿Se usa .env y/o .env.example correctamente?

### 4. Pruebas
- ¿Existen tests automatizados para los módulos críticos?
- ¿Se cubren casos de error y edge cases?

### 5. Despliegue
- ¿El Dockerfile y docker-compose.yml permiten un despliegue sencillo?
- ¿Se documenta el proceso de despliegue?

## Recomendaciones para el agente AI
- Sugerir mejoras en modularidad, documentación y pruebas.
- Detectar duplicidad/confusión en puntos de entrada (main.py, main_docker.py, main_fixed.py).
- Verificar que los comandos de usuario estén documentados y sean consistentes.
- Comprobar que la base de datos es adecuada para el uso esperado.

---

Este archivo puede ser extendido con reglas específicas o ejemplos de buenas prácticas para bots de notificaciones en Python.