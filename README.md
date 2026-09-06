# EcoLogix Systems — TP Integrador (Entrega 1): Del diagnóstico al pipeline validado

**Asignatura:** Desarrollo de Sistemas de Inteligencia Artificial — IADS 3, ORT
**Grupo:** 
Marta Artaza — `martaza-ort` — T-04: riesgo de seguimiento de pedidos
Nombre: Facundo Folgueira,Usuario: Folguee,Lidero: T-02 — Evidencia A.2, segundo modelo
Nombre: Gisella Aramayo, Usuario: giaramayo, Lidero: T-10 — Costo en pesos o dólares
Nombre: Agustina Salatino, Usuario: agustinasalatino, Lidero: T-05 — Fundamento de los tres umbrales
Nombre: Federico Cantero, Usuario: Fedoh, Lidero: T-01 — Evidencia A.2, primer modelo
## Dominio elegido

**EcoLogix Systems** es una distribuidora mediana de productos ecológicos y biodegradables
(bolsas compostables, vajilla de bagazo, sorbetes de papel, envases de cartón, limpieza
ecológica) que vende a comercios y mayoristas. Hoy los pedidos y consultas llegan por
WhatsApp y mail en texto libre y se transcriben a mano a planillas desconectadas
(ventas y almacén): se vende sin stock, se factura mal y nadie sabe dónde está un envío.

El sistema que diseñamos es un **asistente de stock y pedidos**: un normalizador semántico
(LLM) convierte cada mensaje en una intención + parámetros validados con Pydantic, y un
backend determinista (SQL) resuelve contra el stock y los pedidos reales.

Intenciones (árbol cerrado): `CONSULTA_STOCK` · `CREAR_PEDIDO` · `SEGUIMIENTO_PEDIDO` ·
`RECLAMO_ENTREGA` · `OTRO`.

## Estructura del repo

| Archivo | Contenido |
|---|---|
| `TAREAS.md` | Hoja de ruta: setup, reparto de tareas y reglas de trabajo del grupo |
| `informe.md` | Partes A y B completas + narrativa de C.4 y C.5 |
| `schemas.py` | Contrato Pydantic V2 (`Literal`, validadores, modelo anidado) — C.1 |
| `app.py` | Pipeline con API real + Structured Outputs + manejo de errores separado — C.2 |
| `lote.py` | Corre los 6 inputs del dominio y genera `resultados_lote.md` — C.3 |
| `resultados_lote.md` | Tabla de resultados del lote |
| `schema.sql` | Esquema SQL completo (SQLite), incluida la tabla `interacciones` — B.5b |
| `test_schemas.py` | 12 tests del contrato que no consumen API |
| `.env.example` | Variables de entorno sin valores |
| `.gitignore` | Incluye `.env` y `logs/` |
| `CLAUDE.md` | Contexto del proyecto para trabajar con Claude Code |

## Cómo correr

Requiere Python 3.10+.

```bash
# 1. Crear entorno e instalar dependencias
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Credenciales (NUNCA se commitean)
cp .env.example .env
#    editar .env y pegar la key en OPENAI_API_KEY

# 3. Probar el contrato sin gastar créditos
python -m pytest -q test_schemas.py

# 4. Correr un mensaje (usa uno de ejemplo si no se pasa texto)
python app.py
python app.py "Buenas, mandame 20 cajas de vasos de bagazo 12oz para el jueves"
python app.py --tecnica zero "hola como viene el pedido #4521?"

# 5. Correr el lote de 6 inputs y generar la tabla de C.3
python lote.py                                                    # few-shot -> resultados_lote.md
python lote.py --tecnica zero --salida resultados_lote_zero.md    # para comparar en C.4
python lote.py --extra                                            # suma 2 casos opcionales
```

> En macOS/Linux, si `python` no existe en el PATH usar `python3` en los pasos 1 y 3-5.
> Entorno verificado: Python 3.14.6 — `pytest -q test_schemas.py` da **12 passed**,
> `sqlite3 ecologix.db < schema.sql` crea las 9 tablas, y `app.py`/`lote.py` importan
> sin `.env` (toman los defaults). Los pasos 1 a 3 no consumen créditos de API.

Cada corrida se registra en `logs/interacciones.jsonl` (ignorado por Git).

### Variables de entorno (`.env`)

| Variable | Obligatoria | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | sí | API key de OpenAI |
| `OPENAI_MODEL` | no | Modelo a usar (default `gpt-4o-mini`) |
| `OPENAI_TIMEOUT` | no | Timeout en segundos por llamada (default 30) |
| `UMBRAL_CONFIANZA` | no | Confianza mínima para no derivar a humano (default 0.60) |

### Estados posibles del pipeline

`OK` · `VALIDATION_ERROR` (el JSON violó el contrato Pydantic) · `REFUSAL` (el modelo se negó) ·
`ERROR_SALIDA` (truncada/filtrada) · `ERROR_CREDENCIALES` · `ERROR_CUOTA` · `ERROR_RED` ·
`ERROR_PROVEEDOR` · `ERROR_INESPERADO`.

## Seguridad de credenciales

- `.env` está en `.gitignore` desde el primer commit. Solo se sube `.env.example`.
- Si una key se filtró en un commit, **rotarla** (darla de baja y generar una nueva); borrar el
  archivo no alcanza porque queda en el historial.
