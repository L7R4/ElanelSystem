# Plan – Módulo de Caja (minuta 20/10/2026)

Fuente: "Minuta – Reunión Módulo de Caja (CRM)". Se implementa por fases; cada fase se puede
deployar sola.

## Lo que ya existe

| Pieza | Dónde | Estado |
|---|---|---|
| Pagos de cuotas | `PagoCannon` (sales/models.py) – se crea en `Ventas.pagarCuota` | Ya se registra solo |
| Ingresos/egresos manuales | `MovimientoExterno` | Ya existe |
| Saldo del día (efectivo) | `compute_saldo_diario_caja` (sales/services/arqueo.py) | Se calcula al vuelo, filtra por `venta__agencia` |
| Arqueo por billetes | `ArqueoCaja` + `CierreCaja` (`/arqueo/`) + `cierreDeCaja.html` | Un solo tipo, no editable, sin retiros ni adjuntos |
| Lista de arqueos + PDF | `OldArqueosView` (`/arqueo/old/`), `viewPDFArqueo` | Ya existe |
| Archivos | `SupabaseDocumentStorage` (app `documentos`) | Reutilizable para comprobantes |

Problema de base: `PagoCannon` no guarda **en qué sucursal se cobró**; el diario usa la sucursal de
la venta. Eso hay que resolverlo antes del punto 8 (cobro desde otra sucursal) y conviene hacerlo
en la Fase 1.

## Fase 1 – Diario de caja automático (req. 1)
- Agregar `PagoCannon.sucursal_cobro` (FK a `Sucursal`, null) y llenarla en `pagarCuota` con la
  sucursal desde donde se carga el pago.
- Migración de datos: pagos existentes → `sucursal_cobro = venta.agencia`.
- Servicio `get_diario_caja(agencia_id, fecha)` en `sales/services/arqueo.py`: lista unificada
  (pagos + movimientos externos) con ingresos, egresos, método de pago y totales por método.
- `compute_saldo_diario_caja` pasa a filtrar por `sucursal_cobro` y a usar ese servicio.

## Fase 2 – Vista de Cierre de caja por fecha (req. 2, 4 de la lista, 5 de la lista)
- Nuevo modelo `CierreCaja` (agencia, fecha `dd/mm/yyyy`, usuario, estado abierto/cerrado,
  snapshot JSON del diario y totales al cerrar). Uno por sucursal + fecha.
- Botón **Cierre de caja** (en `caja.html`) → vista `/caja/cierre/?agencia=&fecha=` con pestañas:
  1. Diario de caja del día (Fase 1).
  2. Arqueo (Fases 3–4).
  3. Ventas del día en lista; click → modal/expandible con el detalle de pagos de esa venta.
  4. Adjudicados: link/listado al sistema de adjudicaciones existente filtrado por fecha/sucursal.

## Fase 3 – Tipos de arqueo y retiros (req. 3 y 5)
- `ArqueoCaja`: agregar `tipo` (`principal`, `cambio`, extensible), FK `cierre`, y fecha real.
- Modelo `RetiroCaja` (arqueo FK, concepto: honorarios gerente / alquiler / otro, monto,
  descripción, usuario, fecha). Los retiros restan en el arqueo y salen en el PDF.
- Selector de tipo en el formulario de arqueo. El arqueo de cambio guarda el efectivo que queda en
  la sucursal; el resto va al principal (validar que principal + cambio = efectivo del diario −
  retiros).

## Fase 4 – Comprobantes adjuntos (req. 6)
- Modelo `ComprobanteCaja` (FileField con `SupabaseDocumentStorage`, FK opcional a arqueo,
  retiro o cierre/diario, subido_por, fecha).
- Subida desde la vista de cierre y visualización inline (imagen/PDF).

## Fase 5 – Modificación de arqueos con contraseña temporal (req. 4)
- Editar nunca pisa: crea un `ArqueoCaja` nuevo con `original` → FK al arqueo editado y
  `es_modificado=True` ("Arqueo modificado"). El original queda intacto y visible.
- Modelo `CodigoAutorizacion` (objetivo: arqueo o diario, código hasheado, generado_por,
  vence_en, usado). Casa central tiene botón **Generar contraseña** (un solo uso, expira, p.ej.
  30 min). El cajero la ingresa para habilitar la edición.
- Permiso nuevo para quién puede generar (personal de casa central).

## Fase 6 – Descargar/imprimir e historial de cierres (req. 7)
- PDF del cierre completo (diario + arqueos + retiros + ventas + lista de comprobantes),
  reutilizando el generador de `export_arqueo_pdf`.
- Al cerrar se guarda el snapshot; lista `/caja/cierres/` con filtros por sucursal y fecha
  (reemplaza/extiende `listaDeArqueos.html`).

## Fase 7 – Cobro de cuotas desde otra sucursal (punto 8 de la minuta)
Aparece en la minuta como tema tratado, pero no está en la lista de requerimientos y en "Temas a
futuro" figura junto a post venta. **Confirmar si entra en esta etapa.**
- Modelo `SolicitudCobroInterSucursal` (venta, sucursal_solicitante, solicitado_por, estado
  pendiente/aprobada/rechazada/usada, aprobado_por, fechas).
- La sucursal que recibe al cliente pide aprobación desde el detalle de venta; la cajera de la
  sucursal de la venta la ve (badge/notificación) y aprueba.
- Con la solicitud aprobada, `pagarCuota` permite cargar el pago con `sucursal_cobro` = sucursal
  solicitante (entra en su diario de caja), y la solicitud queda `usada`.

## Fuera de alcance
- Módulo de post venta.
- IA integrada en el CRM.

## Decisiones abiertas
1. ¿El punto 8 (cobro inter-sucursal) entra ahora o queda a futuro?
2. Duración y alcance de la contraseña temporal (¿un uso, cuántos minutos?).
3. ¿Qué tipos de arqueo además de principal y cambio?
4. ¿Un cierre cerrado bloquea cargar pagos con esa fecha en esa sucursal?
