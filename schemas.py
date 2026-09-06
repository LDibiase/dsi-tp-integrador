"""
schemas.py — El contrato en código (Parte C.1)

Traduce el System Prompt y el JSON de salida definidos en la Parte B.5 del
informe a un modelo Pydantic V2. Este archivo es la "Capa de Aplicación":
todo lo que el LLM devuelva pasa por acá antes de tocar cualquier sistema
de EcoLogix (stock, pedidos, envíos).

Regla de oro del TP: la IA es el intérprete, la base de datos es la
autoridad. Por eso este esquema NO contiene reglas de negocio (precios,
stock, descuentos): solo define QUÉ puede decir el modelo y en QUÉ formato.

Invariante transversal (criterio 9 de la rúbrica):
    Literal de IntencionEcoLogix == filas de la Matriz de Intenciones (B.3)
                                 == valores posibles en resultados_lote.md (C.3)
Si se agrega o quita una intención, hay que tocar los tres lugares.
"""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

# ---------------------------------------------------------------------------
# 1. Catálogo cerrado de intenciones (árbol de intenciones de EcoLogix)
# ---------------------------------------------------------------------------
IntencionEcoLogix = Literal[
    "CONSULTA_STOCK",       # ¿Hay X? ¿A cuánto está? -> SELECT (lectura, BAJO)
    "CREAR_PEDIDO",         # Mandame N cajas de X   -> INSERT + reserva (escritura, ALTO)
    "SEGUIMIENTO_PEDIDO",   # ¿Cómo viene el pedido 4521? -> SELECT envíos (lectura, MEDIO)
    "RECLAMO_ENTREGA",      # Llegó roto / faltó X   -> ticket + nota de crédito (MEDIO)
    "OTRO",                 # Saludo, spam, hostil, fuera de dominio -> humano (BAJO)
]

# Unidades de venta que existen en el catálogo de EcoLogix.
# Si el cliente escribe "bulto", "pack", "caja", etc. el modelo lo mapea acá.
UnidadVenta = Literal["unidad", "pack", "caja", "rollo", "bulto"]

# Formato de SKU del catálogo (ej: ECO-0042). Solo se acepta si el cliente
# lo escribió; el modelo tiene prohibido inventarlo.
_PATRON_SKU = re.compile(r"^ECO-\d{4}$")


# ---------------------------------------------------------------------------
# 2. Sub-modelo: una línea de pedido / consulta
# ---------------------------------------------------------------------------
class ItemPedido(BaseModel):
    """Un producto mencionado por el cliente. Un mensaje puede traer varios."""

    producto: str = Field(
        description=(
            "Descripción del producto tal como la escribió el cliente, "
            "normalizada en minúsculas y sin cortesías. NO agregar atributos "
            "que el cliente no mencionó (medidas, colores, materiales)."
        )
    )
    cantidad: Optional[int] = Field(
        default=None,
        description="Cantidad numérica pedida. null si el cliente no dijo un número.",
    )
    unidad: Optional[UnidadVenta] = Field(
        default=None,
        description=(
            "Unidad de venta mencionada por el cliente (caja, pack, rollo, bulto, "
            "unidad). null si no la especificó."
        ),
    )
    sku: Optional[str] = Field(
        default=None,
        description=(
            "Código de catálogo con formato ECO-XXXX, SOLO si el cliente lo "
            "escribió textualmente. Nunca inventarlo."
        ),
    )

    @field_validator("producto")
    @classmethod
    def producto_no_vacio(cls, v: str) -> str:
        """El modelo no puede devolver un ítem sin descripción."""
        v = v.strip().lower()
        if not v:
            raise ValueError("El producto no puede estar vacío.")
        return v

    @field_validator("cantidad")
    @classmethod
    def cantidad_en_rango(cls, v: Optional[int]) -> Optional[int]:
        """
        Rechaza rangos inválidos: EcoLogix vende por bultos, un pedido de 0 o
        de 50.000 cajas es casi seguro un error de extracción (o un ataque).
        El límite superior es una regla de negocio provisoria — discutir en grupo.
        """
        if v is None:
            return v
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        if v > 10_000:
            raise ValueError("Cantidad fuera de rango operativo (máximo 10.000 por línea).")
        return v

    @field_validator("sku")
    @classmethod
    def sku_normalizado(cls, v: Optional[str]) -> Optional[str]:
        """Sanitiza el SKU (espacios, minúsculas, guiones raros) y valida el formato."""
        if v is None:
            return v
        limpio = re.sub(r"[\s_]+", "", v.strip().upper()).replace("–", "-")
        if not limpio:
            return None
        if not _PATRON_SKU.match(limpio):
            raise ValueError(f"SKU '{v}' no respeta el formato ECO-XXXX del catálogo.")
        return limpio


# ---------------------------------------------------------------------------
# 3. Modelo principal: la salida del LLM para un mensaje entrante
# ---------------------------------------------------------------------------
class MensajeClasificado(BaseModel):
    """
    Contrato de salida del normalizador semántico (Parte B.5c -> C.1).

    Todo campo que el cliente no haya dicho explícitamente debe ser null.
    El backend determinista decide qué hacer con los nulls (pedir el dato,
    usar el default del cliente, derivar a un humano).
    """

    intencion: IntencionEcoLogix = Field(
        description="Categoría raíz del mensaje según el árbol de intenciones de EcoLogix."
    )
    items: list[ItemPedido] = Field(
        default_factory=list,
        description=(
            "Productos mencionados. Lista vacía si el mensaje no nombra ningún "
            "producto (por ejemplo, un seguimiento de pedido)."
        ),
    )
    nro_pedido: Optional[str] = Field(
        default=None,
        description="Número de pedido mencionado por el cliente, solo dígitos. null si no lo dijo.",
    )
    cliente_declarado: Optional[str] = Field(
        default=None,
        description=(
            "Nombre del comercio o persona con que se presenta el remitente "
            "(ej: 'Café Mundo', 'Dietética Sol'). null si no se identifica."
        ),
    )
    direccion_entrega: Optional[str] = Field(
        default=None,
        description=(
            "Lugar de entrega mencionado, textual (ej: 'local de Palermo'). "
            "null si no lo dijo. NO completar con la dirección habitual."
        ),
    )
    fecha_entrega_deseada: Optional[str] = Field(
        default=None,
        description=(
            "Expresión temporal textual del cliente (ej: 'el jueves', 'antes del 15'). "
            "No convertir a fecha: eso lo resuelve el backend con el timestamp del mensaje."
        ),
    )
    motivo_reclamo: Optional[str] = Field(
        default=None,
        description=(
            "Solo para RECLAMO_ENTREGA: qué pasó, en pocas palabras "
            "(ej: 'cajas rotas', 'faltante', 'demora'). null en otras intenciones."
        ),
    )
    confianza: float = Field(
        description="Certeza del modelo en la clasificación de la intención, de 0.0 a 1.0."
    )

    # --- Validadores de campo -------------------------------------------------

    @field_validator("nro_pedido")
    @classmethod
    def limpiar_nro_pedido(cls, v: Optional[str]) -> Optional[str]:
        """
        Los clientes escriben '#4521', 'pedido N° 4521', '4.521'. Se dejan
        solo los dígitos y se exige el rango de longitud que usa EcoLogix (4 a 8).
        """
        if v is None:
            return v
        digitos = "".join(ch for ch in v if ch.isdigit())
        if not digitos:
            return None  # el modelo puso algo que no era un número: se descarta
        if not 4 <= len(digitos) <= 8:
            raise ValueError(
                f"Número de pedido '{v}' inválido: se esperan entre 4 y 8 dígitos."
            )
        return digitos

    @field_validator("confianza")
    @classmethod
    def confianza_en_rango(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("La confianza debe estar entre 0.0 y 1.0.")
        return round(v, 2)

    @field_validator("cliente_declarado", "direccion_entrega", "fecha_entrega_deseada", "motivo_reclamo")
    @classmethod
    def vacio_es_null(cls, v: Optional[str]) -> Optional[str]:
        """Un string vacío o 'null' escrito como texto se convierte en None real."""
        if v is None:
            return v
        v = v.strip()
        return None if v == "" or v.lower() in {"null", "none", "n/a"} else v

    # --- Validador cruzado (regla de completitud del contrato) ----------------

    @model_validator(mode="after")
    def coherencia_intencion_datos(self) -> "MensajeClasificado":
        """
        Reglas que dependen de más de un campo:
        - Un pedido sin ítems no es un pedido ejecutable -> se rechaza el contrato
          (el backend pedirá aclaración). Es el caso típico del input ambiguo
          "mandame lo de siempre".
        - Un motivo de reclamo solo tiene sentido en RECLAMO_ENTREGA; en otra
          intención es señal de extracción confusa y se descarta (no se rechaza).
        """
        if self.intencion == "CREAR_PEDIDO" and not self.items:
            raise ValueError(
                "CREAR_PEDIDO requiere al menos un ítem con producto identificable."
            )
        if self.intencion != "RECLAMO_ENTREGA" and self.motivo_reclamo is not None:
            self.motivo_reclamo = None
        return self


__all__ = [
    "IntencionEcoLogix",
    "UnidadVenta",
    "ItemPedido",
    "MensajeClasificado",
    "ValidationError",
]
