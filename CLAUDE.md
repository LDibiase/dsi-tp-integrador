# Contexto del proyecto para Claude Code

Este repo es la **Entrega 1 del TP Integrador** de "Desarrollo de Sistemas de IA" (IADS 3, ORT).
Trabajo grupal. El enunciado completo está en el Project de claude.ai
(`TP_Integrador_Entrega1_Clases_1a3.pdf`); lo esencial está resumido acá.

## Qué es esto

Sistema de stock y pedidos para **EcoLogix Systems** (distribuidora de productos ecológicos).
Patrón híbrido de la cátedra: el LLM es el "mozo" (normaliza lenguaje natural → JSON),
el backend determinista es el "chef" (valida con Pydantic y resuelve contra SQL).
**La IA es el intérprete, la base de datos es la autoridad.**

## Archivos y a qué parte del TP responden

- `informe.md` — Partes A (diagnóstico, PEAS, tiktoken) y B (matriz de intenciones, decisión reglas/LLM,
  JSON + SQL + System Prompt, flujo, hipótesis) + narrativa C.4/C.5. Cerrado para la Entrega 1.
- `schemas.py` — C.1. Contrato Pydantic V2. `IntencionEcoLogix` es un `Literal` de 5 valores.
- `app.py` — C.2. Pipeline: `.env` → OpenAI con `response_format` json_schema estricto → Pydantic → enrutador.
- `lote.py` — C.3. 6 inputs fijos → `resultados_lote.md`. `--tecnica zero|few` para el experimento de C.4.
- `schema.sql` — B.5b. SQLite, probado. Incluye la tabla `interacciones`.
- `test_schemas.py` — tests del contrato sin API.

## Invariantes que NO se pueden romper (criterio 9 de la rúbrica: coherencia transversal)

1. `Literal` de `schemas.py` == filas de la Matriz B.3 en `informe.md` == valores en `resultados_lote.md`
   == intenciones nombradas en el System Prompt de `app.py`. Si se agrega/quita una intención, tocar los 4.
2. `UnidadVenta` de `schemas.py` == valores de `productos.unidad_venta` en `schema.sql`.
3. El JSON de salida de ejemplo en informe.md B.5 debe validar contra `MensajeClasificado`.
4. El LLM nunca ve precios, stock ni decide escrituras. Toda regla de negocio va en código o SQL.

## Reglas de seguridad (penalizaciones del TP)

- `.env` NUNCA se commitea (ya está en `.gitignore`). Solo `.env.example` sin valores. Una key en el
  historial cuesta −15 puntos y hay que rotarla.
- Commits incrementales y con autor real (se evalúa "quién hizo qué"). Nada de un único commit final.

## Convenciones

- Código y comentarios en español rioplatense, nombres de variables en español (como la cátedra).
- Proveedor: OpenAI, modelo `gpt-4o-mini` (configurable en `.env`). Si se cambia de proveedor,
  adaptar `llamar_modelo()` y los `except` de `procesar_mensaje()` en `app.py`.
- No agregar restricciones (`ge`, `pattern`, `min_length`) en `Field(...)`: el modo `strict` de
  Structured Outputs puede rechazarlas. Las reglas van en `@field_validator`.
- Antes de commitear: `python -m pytest -q test_schemas.py`.

## Pendientes (estado al 2026-09-07)

La Entrega 1 está cerrada: integrantes completos, A.2 con la respuesta real de dos modelos y
lo inventado marcado, lote de C.3 y comparación de C.4 corridos contra la API real, y las
7 "Decisiones abiertas" resueltas o postergadas con fundamento. No quedan marcadores ⚠️.

- [ ] Confirmar que el docente esté agregado como colaborador del repo.
