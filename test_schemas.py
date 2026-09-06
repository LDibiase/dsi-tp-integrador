"""
test_schemas.py — Pruebas locales del contrato (no consumen API).

Correr con:  python -m pytest -q      (o simplemente: python test_schemas.py)

Simulan salidas que el modelo PODRÍA devolver y verifican que Pydantic
acepte las correctas y rechace las que violan el contrato.
"""

import json

import pytest
from pydantic import ValidationError

from schemas import MensajeClasificado

BASE = {
    "intencion": "CONSULTA_STOCK",
    "items": [{"producto": "bolsas compostables 40x50", "cantidad": None, "unidad": None, "sku": None}],
    "nro_pedido": None,
    "cliente_declarado": None,
    "direccion_entrega": None,
    "fecha_entrega_deseada": None,
    "motivo_reclamo": None,
    "confianza": 0.9,
}


def _con(**cambios):
    d = json.loads(json.dumps(BASE))
    d.update(cambios)
    return d


def test_salida_correcta_valida():
    m = MensajeClasificado.model_validate(BASE)
    assert m.intencion == "CONSULTA_STOCK"
    assert m.items[0].producto == "bolsas compostables 40x50"


def test_intencion_fuera_del_literal_se_rechaza():
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(intencion="MARCAR_COMO_PAGADO"))


def test_nro_pedido_se_limpia():
    m = MensajeClasificado.model_validate(_con(intencion="SEGUIMIENTO_PEDIDO", items=[], nro_pedido="N° 4.521"))
    assert m.nro_pedido == "4521"


def test_nro_pedido_longitud_invalida():
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(intencion="SEGUIMIENTO_PEDIDO", items=[], nro_pedido="12"))


def test_pedido_sin_items_se_rechaza():
    # Caso ambiguo "mandame lo de siempre"
    with pytest.raises(ValidationError) as exc:
        MensajeClasificado.model_validate(_con(intencion="CREAR_PEDIDO", items=[]))
    assert "al menos un ítem" in str(exc.value)


def test_cantidad_fuera_de_rango():
    item = {"producto": "bolsas", "cantidad": 50000, "unidad": "caja", "sku": None}
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(intencion="CREAR_PEDIDO", items=[item]))


def test_cantidad_cero():
    item = {"producto": "bolsas", "cantidad": 0, "unidad": "caja", "sku": None}
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(intencion="CREAR_PEDIDO", items=[item]))


def test_sku_se_normaliza_y_valida():
    item = {"producto": "vasos", "cantidad": 2, "unidad": "caja", "sku": " eco-0042 "}
    m = MensajeClasificado.model_validate(_con(intencion="CREAR_PEDIDO", items=[item]))
    assert m.items[0].sku == "ECO-0042"
    item_malo = {"producto": "vasos", "cantidad": 2, "unidad": "caja", "sku": "ABC123"}
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(intencion="CREAR_PEDIDO", items=[item_malo]))


def test_confianza_fuera_de_rango():
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(confianza=1.7))


def test_strings_vacios_se_vuelven_null():
    m = MensajeClasificado.model_validate(_con(cliente_declarado="", direccion_entrega="N/A"))
    assert m.cliente_declarado is None and m.direccion_entrega is None


def test_motivo_reclamo_fuera_de_reclamo_se_descarta():
    m = MensajeClasificado.model_validate(_con(motivo_reclamo="cajas rotas"))
    assert m.motivo_reclamo is None


def test_unidad_fuera_del_catalogo_se_rechaza():
    item = {"producto": "vasos", "cantidad": 2, "unidad": "docena", "sku": None}
    with pytest.raises(ValidationError):
        MensajeClasificado.model_validate(_con(intencion="CREAR_PEDIDO", items=[item]))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
