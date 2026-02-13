from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from django.db.models import Q, Sum, FloatField, Value
from django.db.models.functions import Coalesce

from sales.models import PagoCannon, MovimientoExterno, Sucursal


BILLETES: List[int] = [20000, 10000, 2000, 1000, 500, 200, 100, 50, 20, 10]

# Métodos que consideramos "caja efectivo"
CASH_METHOD_ALIASES = ("efectivo", "contado")


def today_fragment_ddmmyyyy() -> str:
    # dd/mm/yyyy (para buscar en CharField fecha)
    return datetime.now().strftime("%d/%m/%Y")


def _q_cash_metodo(field_prefix: str) -> Q:
    """
    Construye Q(... OR ...) para metodo alias efectivo/contado.
    field_prefix: "metodo_pago" o "metodoPago"
    """
    q = Q()
    for a in CASH_METHOD_ALIASES:
        q |= Q(**{f"{field_prefix}__alias__iexact": a})
    return q


def get_allowed_agencias(request) -> List[Sucursal]:
    try:
        if getattr(request.user, "is_superuser", False):
            return list(Sucursal.objects.all())
        return list(request.user.sucursales.all())
    except Exception:
        return []


def validate_agencia_allowed(request, agencia_id: int) -> Optional[Sucursal]:
    allowed = get_allowed_agencias(request)
    for s in allowed:
        if int(s.id) == int(agencia_id):
            return s
    return None


def compute_saldo_diario_caja(agencia_id: int, fecha_ddmmyyyy: Optional[str] = None) -> float:
    dia = (fecha_ddmmyyyy or today_fragment_ddmmyyyy()).strip() or today_fragment_ddmmyyyy()

    pagos_qs = (
        PagoCannon.objects
        .select_related("metodo_pago", "venta", "venta__agencia")
        .filter(venta__agencia_id=agencia_id)
        .filter(fecha__startswith=dia)
        .filter(_q_cash_metodo("metodo_pago"))
    )

    externos_qs = (
        MovimientoExterno.objects
        .select_related("metodoPago", "agencia")
        .filter(agencia_id=agencia_id)
        .filter(fecha__startswith=dia)
        .filter(_q_cash_metodo("metodoPago"))
    )

    pagos_total = float(
        pagos_qs.aggregate(
            total=Coalesce(
                Sum("monto", output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            )
        )["total"] or 0.0
    )

    ext_ing = float(
        externos_qs.filter(movimiento__iexact="ingreso").aggregate(
            total=Coalesce(
                Sum("dinero", output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            )
        )["total"] or 0.0
    )

    ext_egr = float(
        externos_qs.filter(movimiento__iexact="egreso").aggregate(
            total=Coalesce(
                Sum("dinero", output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            )
        )["total"] or 0.0
    )

    return pagos_total + ext_ing - ext_egr
