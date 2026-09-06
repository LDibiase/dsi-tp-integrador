-- schema.sql — Esquema de la base de datos de EcoLogix (Parte B.5b)
-- Dialecto: SQLite (para poder correrlo sin instalar nada: `sqlite3 ecologix.db < schema.sql`).
-- Migrable a PostgreSQL cambiando INTEGER PRIMARY KEY por SERIAL y TEXT por VARCHAR/JSONB.
--
-- Principio: estas tablas son la FUENTE DE VERDAD. El LLM nunca las escribe
-- directamente; solo el backend, después de validar el contrato con Pydantic.

-- ---------------------------------------------------------------------------
-- Entidades principales del dominio
-- ---------------------------------------------------------------------------
CREATE TABLE clientes (
    id                  INTEGER PRIMARY KEY,
    razon_social        TEXT NOT NULL,
    cuit                TEXT UNIQUE,                 -- 11 dígitos, validado por código
    telefono_whatsapp   TEXT UNIQUE,                 -- clave para resolver "remitente -> cliente"
    email               TEXT,
    direccion_default   TEXT,                        -- se usa si el mensaje no trae direccion_entrega
    activo              INTEGER NOT NULL DEFAULT 1,
    creado_en           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE productos (
    sku                 TEXT PRIMARY KEY,            -- formato ECO-XXXX (ver validador en schemas.py)
    nombre              TEXT NOT NULL,               -- "Vaso de bagazo 12 oz"
    categoria           TEXT NOT NULL,               -- vajilla | bolsas | envases | limpieza | sorbetes
    material            TEXT,                        -- bagazo | PLA | cartón | papel ...
    unidad_venta        TEXT NOT NULL,               -- unidad | pack | caja | rollo | bulto  (= UnidadVenta)
    unidades_por_bulto  INTEGER,
    precio_lista        REAL NOT NULL,               -- el LLM NUNCA ve ni decide precios
    activo              INTEGER NOT NULL DEFAULT 1
);

-- Alias/jerga con que los clientes nombran los productos ("vasitos", "bolsas verdes").
-- Hoy: mapeo determinista por texto. Unidad 3: se reemplaza/complementa con embeddings.
CREATE TABLE producto_alias (
    id                  INTEGER PRIMARY KEY,
    sku                 TEXT NOT NULL REFERENCES productos(sku),
    alias               TEXT NOT NULL,
    UNIQUE (sku, alias)
);

CREATE TABLE stock (
    sku                 TEXT NOT NULL REFERENCES productos(sku),
    deposito            TEXT NOT NULL DEFAULT 'central',
    cantidad_disponible INTEGER NOT NULL DEFAULT 0,
    cantidad_reservada  INTEGER NOT NULL DEFAULT 0,  -- reservado por pedidos confirmados no despachados
    actualizado_en      TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (sku, deposito)
);

CREATE TABLE pedidos (
    id                  INTEGER PRIMARY KEY,         -- el "nro_pedido" que el cliente cita
    cliente_id          INTEGER NOT NULL REFERENCES clientes(id),
    estado              TEXT NOT NULL DEFAULT 'BORRADOR'
                        CHECK (estado IN ('BORRADOR','CONFIRMADO','PREPARANDO','DESPACHADO','ENTREGADO','CANCELADO')),
    direccion_entrega   TEXT NOT NULL,
    fecha_entrega_solicitada TEXT,                   -- ISO 8601, resuelta por el backend (no por el LLM)
    interaccion_origen_id INTEGER REFERENCES interacciones(id),  -- trazabilidad: qué mensaje lo generó
    creado_en           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE pedido_items (
    id                  INTEGER PRIMARY KEY,
    pedido_id           INTEGER NOT NULL REFERENCES pedidos(id),
    sku                 TEXT NOT NULL REFERENCES productos(sku),
    cantidad            INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario     REAL NOT NULL                -- congelado al confirmar; viene de productos, no del mensaje
);

CREATE TABLE envios (
    id                  INTEGER PRIMARY KEY,
    pedido_id           INTEGER NOT NULL REFERENCES pedidos(id),
    transportista       TEXT,
    tracking            TEXT,
    estado              TEXT NOT NULL DEFAULT 'PENDIENTE'
                        CHECK (estado IN ('PENDIENTE','EN_CAMINO','ENTREGADO','INCIDENCIA')),
    despachado_en       TEXT,
    entregado_en        TEXT
);

CREATE TABLE reclamos (
    id                  INTEGER PRIMARY KEY,
    pedido_id           INTEGER REFERENCES pedidos(id),
    cliente_id          INTEGER NOT NULL REFERENCES clientes(id),
    motivo              TEXT NOT NULL,               -- viene de motivo_reclamo del contrato
    estado              TEXT NOT NULL DEFAULT 'ABIERTO'
                        CHECK (estado IN ('ABIERTO','EN_REVISION','RESUELTO','RECHAZADO')),
    nota_credito_monto  REAL,                        -- la define una persona, nunca el LLM
    interaccion_origen_id INTEGER REFERENCES interacciones(id),
    creado_en           TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- Tabla de interacciones: qué intención detectó el LLM y qué respondió el sistema
-- (auditoría del "mozo": permite medir Performance del PEAS y detectar drift)
-- ---------------------------------------------------------------------------
CREATE TABLE interacciones (
    id                  INTEGER PRIMARY KEY,
    canal               TEXT NOT NULL CHECK (canal IN ('whatsapp','email','web','interno')),
    remitente_id        TEXT NOT NULL,               -- teléfono / email / usuario, tal como llegó
    cliente_id          INTEGER REFERENCES clientes(id),  -- NULL si el remitente no está registrado
    id_mensaje_canal    TEXT,                        -- id externo (wamid, Message-ID) para idempotencia
    texto_original      TEXT NOT NULL,
    adjuntos_json       TEXT,                        -- lista de URLs/ids de adjuntos (JSON)
    recibido_en         TEXT NOT NULL,               -- timestamp del canal (para fechas relativas)

    -- Lo que produjo el LLM (capa probabilística)
    modelo              TEXT,                        -- gpt-4o-mini, etc.
    tecnica_prompt      TEXT,                        -- zero | few
    intencion_detectada TEXT,                        -- valor del Literal, o NULL si no hubo JSON
    parametros_json     TEXT,                        -- el JSON crudo devuelto por el modelo
    confianza           REAL,
    tokens_entrada      INTEGER,
    tokens_salida       INTEGER,
    latencia_ms         INTEGER,

    -- Lo que decidió el backend (capa determinista)
    estado_pipeline     TEXT NOT NULL,               -- OK | VALIDATION_ERROR | REFUSAL | ERROR_RED | ...
    error_detalle       TEXT,
    accion_backend      TEXT,                        -- SELECT stock / INSERT pedido / DERIVAR_A_HUMANO ...
    respuesta_enviada   TEXT,                        -- texto final al cliente (lo redacta el LLM en el paso 4 de B.6)
    derivado_a_humano   INTEGER NOT NULL DEFAULT 0,
    procesado_en        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_interacciones_cliente ON interacciones(cliente_id, recibido_en);
CREATE INDEX idx_interacciones_intencion ON interacciones(intencion_detectada, estado_pipeline);
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id, estado);
