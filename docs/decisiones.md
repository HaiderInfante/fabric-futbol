# Registro de decisiones de arquitectura (ADR)

Formato breve: contexto → decisión → alternativas descartadas → consecuencias.

---

## ADR-001 — Monorepo con carpeta `fabric/` sincronizada

- **Fecha:** 2026-09-28
- **Contexto:** hay artefactos de dos tipos: ítems de Fabric (notebooks, pipelines, lakehouses,
  modelo semántico) y código local (clientes HTTP, transformaciones testeables, scripts, CI).
- **Decisión:** un solo repositorio. La integración Git de `ws_futbol_dev` se limita a la carpeta
  `fabric/` y el resto del repo queda fuera de su alcance.
- **Alternativas:** conectar Fabric a la raíz del repo (mezclaría ítems con código local y Fabric
  intentaría interpretar carpetas ajenas); usar dos repositorios (duplicaría CI y complicaría los
  PR que tocan código y notebooks a la vez).
- **Consecuencias:** los PR pueden cambiar a la vez la lógica en `src/` y el notebook que la usa.
  La carpeta `fabric/` solo se edita a través de Fabric o partiendo de una plantilla generada por
  Fabric.

## ADR-002 — Secretos en `.env` local y GitHub Secrets en CI

- **Fecha:** 2026-09-28
- **Contexto:** dos APIs requieren key y el repositorio es público.
- **Decisión:** las keys viven solo en `.env` (ignorado por Git). `.env.example` documenta las
  variables sin valores. En CI se usarán GitHub Secrets. Dentro de Fabric las keys se leerán desde
  Azure Key Vault o una conexión, a definir en la Fase 2.
- **Alternativas:** keys en un notebook o en `parameter.yml` (quedarían expuestas en Git).
- **Consecuencias:** cada desarrollador crea su propio `.env`. `check_access.py` nunca imprime
  valores de keys.

## ADR-003 — API-Football mediante registro directo en api-sports.io

- **Fecha:** 2026-09-28
- **Contexto:** API-Football se ofrece directamente (api-sports.io) y a través de RapidAPI, con
  distinta URL base y distinto header de autenticación.
- **Decisión:** registro directo. URL base `https://v3.football.api-sports.io` y header
  `x-apisports-key`.
- **Consecuencias:** el endpoint `/status` permite consultar el uso diario sin consumir cuota; lo
  usaremos para sincronizar `ctl_api_budget` en la Fase 2. Detalle importante: api-sports puede
  responder HTTP 200 con errores en el campo `errors`, así que el cliente debe revisar ese campo
  además del código HTTP.

## ADR-004 — `main` protegida y flujo de commits desde Fabric

- **Fecha:** 2026-09-28
- **Contexto:** `ws_futbol_dev` está conectado a `main`, que se protegerá con un ruleset que exige
  PR. Según Microsoft Learn, para hacer commit desde un workspace hacia su rama conectada, la
  política de la rama debe permitir commits directos. Por tanto, con `main` protegida, DEV **no
  podrá** hacer commit directo.
- **Decisión:** DEV solo recibe cambios con **Update from Git**. Los ítems nuevos o modificados en
  Fabric llegan a `main` por una de estas dos vías:
  1. **Branch out to another workspace**: se crea un workspace de feature conectado a una rama
     `feature/*`, se trabaja y se hace commit allí, y luego se abre un PR a `main`.
  2. **Commit to new branch** desde el panel Source control de DEV, para cambios puntuales. Crea
     una rama nueva con los cambios sin cambiar la conexión de DEV. Luego se abre un PR.
- **Alternativas:** dejar `main` sin protección (contradice el flujo definido en CLAUDE.md) o
  añadir al administrador al bypass list (anula el propósito de la protección).
- **Consecuencias:** se practica el flujo de ramas de Fabric que evalúa el DP-700. Los ítems que
  sirvan de plantilla (regla 5 de CLAUDE.md) se crearán con alguna de estas dos vías.
