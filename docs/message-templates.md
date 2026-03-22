# Message Templates

All messages are produced by `formatter.py` — a pure module with no I/O. Every function takes data dicts and returns a string.

---

## Match Notification (basic)

**Function:** `format_match_summary(player_name, parsed, *, pro_team=None)`

**Source:** `parse_match_for_puuid()` output

```
🌟 PRO · G2
✅ VICTORIA — Orianna

👤 Caps#EUW
⚔️  KDA: 8/2/12  (ratio 10.00)
🎯 Modo: Ranked Solo/Duo
⏱️  Duración: 32m 14s
🔗 ID: EUW1_7123456789
```

For personal accounts (no `pro_team`):
```
🎮 Partida
❌ DERROTA — Graves

👤 LaBísica#EUW
⚔️  KDA: 3/7/5  (ratio 1.14)
🎯 Modo: Normal Draft
⏱️  Duración: 28m 45s
🔗 ID: EUW1_7123456780
```

---

## Match Notification (extended stats)

**Function:** `format_match_summary_with_stats(player_name, parsed, full_participant, *, pro_team=None)`

Adds CS, gold, damage, and vision to the basic format:

```
🌟 PRO · T1
✅ VICTORIA — Azir

👤 Hide on bush#KR1
⚔️  KDA: 12/1/8  (ratio 20.00)
🎯 Modo: Ranked Solo/Duo
⏱️  Duración: 35m 22s

🌾 CS: 312   💰 Oro: 18,400
💥 Daño: 42,100   👁️  Visión: 45
🔗 ID: KR_7123456789
```

---

## Aggregated Stats (`/stats`)

**Function:** `format_aggregated_stats(player_name, agg, *, pro_team=None, role=None)`

**Source:** `aggregate_stats()` output

```
📊 Estadísticas
👤 LaBísica#EUW

🎮 Partidas: 5  (3V / 2D)
🔥 Winrate: 60.0%
⚔️  KDA medio: 6.0/3.0/8.0  (ratio 4.67)
🏆 Campeón más jugado: Graves

🌾 CS/min: 6.2
💰 Oro medio: 13,400
💥 Daño medio: 22,800
👁️  Visión media: 28.0

⭐ Performance score: 58.4/100
🎆 Pentas: 1
```

For a pro with role:
```
🌟 PRO · G2 ⚡
👤 Caps#EUW
...
```

Role emojis: `🛡️ TOP` · `🌲 JGL` · `⚡ MID` · `🏹 BOT` · `💊 SUP`

Winrate emoji: `🔥` ≥60% · `✅` ≥50% · `❌` <50%

---

## Player Ranking

**Function:** `format_player_ranking(ranking, title="🏆 Ranking de jugadores")`

**Source:** `rank_players()` output

```
🏆 Ranking de jugadores

🥇 Faker#KR1  —  score 82.3
🥈 Caps#EUW  —  score 71.5
🥉 Bjergsen#NA1  —  score 64.2
4. Humanoid#EUW  —  score 58.1
```

---

## Account Status (`/status`)

**Function:** `format_status(user)`

```
👤 Cuenta: LaBísica#EUW (euw1)
🔔 Notificaciones: ✅ activas
🕐 Última poll: 2026-03-22 01:00:00
🎮 Última partida: EUW1_7123456789
```

With notifications paused:
```
🔔 Notificaciones: ⏸️  pausadas
```

---

## Pro List (`/list_pros`)

**Function:** `format_pro_list(pros)`

```
🌟 Pros trackeados:

  [1] Faker#KR1 (kr) · T1 ⚡
  [2] Caps#EUW (euw1) · G2 ⚡
  [3] Gumayusi#T1 (kr) · T1 🏹
  [4] BrokenBlade#EUW (euw1) · G2 🛡️
```

Empty list:
```
No hay pros trackeados. Usa /add_pro GameName#TAG region
```

---

## Help (`/start`, `/help`)

**Function:** `format_help()`

```
🤖 LoLNotifierBot

📌 Tu cuenta:
  /set_summoner GameName#TAG region
    ej: /set_summoner LaBísica#EUW euw1
  /status — ver tu configuración
  /stats — estadísticas de tus últimas 5 partidas
  /toggle — activar/pausar notificaciones

🌟 Pros:
  /add_pro GameName#TAG region
    ej: /add_pro Caps#EUW euw1
  /list_pros — ver pros trackeados
  /remove_pro <id>
  /load_pros — cargar dataset oficial

🗺️  Regiones: na1 · euw1 · kr · la1 · la2
              eun1 · br1 · jp1 · tr1
```

---

## Queue Labels

| Queue ID | Label |
|---|---|
| 420 | Ranked Solo/Duo |
| 440 | Ranked Flex |
| 400 | Normal Draft |
| 430 | Normal Blind |
| 450 | ARAM |
| 700 | Clash |
| 900 | URF |
| 1020 | One for All |
| 1300 | Nexus Blitz |
| 1400 | Ultimate Spellbook |
| 0 | Custom |
| other | Queue {id} |
