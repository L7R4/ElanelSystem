"""
Test end-to-end del flujo del cajero (rol "Administrativa"):

    1. Alta de cliente
    2. Alta de venta para ese cliente
    3. Cobro de cuotas (total y parcial) + verificación en caja
    4. Adjudicación por SORTEO
    5. Adjudicación por NEGOCIACIÓN

Usa las mismas URLs y los mismos payloads JSON que arma el frontend
(redirectNewCustomer.js, form_create_sale.js, manejoCuotas.js, form_create_adju.js).
Corre sobre la base de test que crea Django, nunca sobre la base real.

    python manage.py test sales.test_flujo_cajero -v 2
"""
import datetime
import json
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission

from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from products.models import Plan, Products
from sales.models import (
    CoeficientesListadePrecios, CuentaCobranza, MetodoPago, PagoCannon, TasaInteres, Ventas,
)
from sales.utils import getCampaniaActual
from users.models import Cliente, Sucursal, Usuario


def _fake_dolar(request):
    return JsonResponse({"oficial": {"compra": 1400, "venta": 1450}})


HOY = datetime.date.today().strftime("%d/%m/%Y")

# Valores de la venta de prueba (24 cuotas mensuales)
IMPORTE = 2_400_000
ANTICIPO = 100_000
PRIMER_CUOTA = 120_000
IMPORTE_X_CUOTA = 240_000
NRO_CUOTAS = 24


@patch("sales.views.cotizaciones_dolar", _fake_dolar)  # el detalle de venta consulta una API externa
class FlujoCajeroTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.sucursal = Sucursal.objects.create(
            direccion="calle 1", hora_apertura="08:00", provincia="corrientes", localidad="goya",
        )
        cls.gerente = Usuario.objects.create_user(
            email="gerente@test.com", nombre="Gerente Test", dni="30000001", rango="Gerente sucursal",
            password="x")
        cls.sucursal.gerente = cls.gerente
        cls.sucursal.save()

        cls.supervisor = Usuario.objects.create_user(
            email="super@test.com", nombre="Supervisor Test", dni="30000002", rango="Supervisor", password="x")
        cls.vendedor = Usuario.objects.create_user(
            email="vende@test.com", nombre="Vendedor Test", dni="30000003", rango="Vendedor", password="x")
        cls.vendedor.supervisores_a_cargo = cls.supervisor
        cls.vendedor.save()

        # Cajero: mismo grupo/permisos que "Administrativa" en la base real
        cls.cajero = Usuario.objects.create_user(
            email="cajero@test.com", nombre="Cajero Test", dni="30000004", rango="Administrativa", password="x")
        grupo, _ = Group.objects.get_or_create(name="Administrativa")
        for app, codename in [("sales", "my_ver_caja"), ("sales", "my_anular_cuotas"), ("users", "my_ver_clientes")]:
            perm = Permission.objects.filter(content_type__app_label=app, codename=codename).first()
            if perm:
                grupo.permissions.add(perm)
        cls.cajero.groups.add(grupo)
        for u in (cls.supervisor, cls.vendedor, cls.cajero, cls.gerente):
            u.sucursales.add(cls.sucursal)

        plan = Plan.objects.create(valor_nominal=IMPORTE, suscripcion=ANTICIPO, primer_cuota=PRIMER_CUOTA)
        cls.producto = Products.objects.create(tipo_de_producto="Moto", nombre="Moto 110cc", plan=plan)

        cls.efectivo = MetodoPago.objects.create(alias="Efectivo")
        cls.transferencia = MetodoPago.objects.create(alias="Transferencia")
        cls.credito = MetodoPago.objects.create(alias="Credito")  # obligatorio para adjudicar por sorteo
        cls.cobrador = CuentaCobranza.objects.create(alias="Oficina")
        TasaInteres.objects.create(valor=70, es_default=True)
        TasaInteres.objects.create(valor=80)
        CoeficientesListadePrecios.objects.create(valor_nominal=IMPORTE, cuota=24, porcentage=100)

    def setUp(self):
        self.client.force_login(self.cajero)

    # ------------------------------------------------------------------ helpers
    def post_json(self, url, body):
        resp = self.client.post(url, data=json.dumps(body), content_type="application/json")
        self.assertEqual(resp.status_code, 200, f"POST {url} -> {resp.status_code}")
        return resp.json()

    def crear_cliente(self, nombre, dni, tel="3794123456"):
        url = reverse("users:create_customer")
        self.assertEqual(self.client.get(url).status_code, 200)
        data = self.post_json(url, {
            "nombre": nombre, "dni": dni, "domic": "san martin 123", "loc": "goya", "prov": "corrientes",
            "cod_postal": "3450", "tel": tel, "estado_civil": "soltero", "fec_nacimiento": "01/01/1990",
            "ocupacion": "comerciante",
        })
        self.assertTrue(data["success"], data)
        return Cliente.objects.get(dni=dni)

    def crear_venta(self, cliente, nro_contrato="1000123"):
        url = reverse("sales:create_sale", args=[cliente.pk])
        self.assertEqual(self.client.get(url).status_code, 200)

        # El form pide vendedores/supervisores de la agencia elegida
        vs = self.post_json(reverse("sales:requestVendedores_Supervisores"), {"agencia": self.sucursal.id})
        self.assertIn(self.vendedor.id, [v["id"] for v in vs["vendedores"]])
        self.assertIn(self.supervisor.id, [s["id"] for s in vs["supervisores"]])

        intereses = IMPORTE_X_CUOTA * NRO_CUOTAS - IMPORTE
        data = self.post_json(url, {
            "agencia": str(self.sucursal.id), "producto": str(self.producto.id),
            "tipo_producto": "Moto", "paquete": "Estandar", "campania": getCampaniaActual(),
            "vendedor": str(self.vendedor.id), "supervisor": str(self.supervisor.id),
            "modalidad": "Mensual", "fecha": HOY,
            "nro_contrato_1": nro_contrato, "nro_orden_1": nro_contrato[-3:],
            "importe": str(IMPORTE), "anticipo": str(ANTICIPO), "primer_cuota": str(PRIMER_CUOTA),
            "nro_cuotas": str(NRO_CUOTAS), "importe_x_cuota": str(IMPORTE_X_CUOTA),
            "intereses_generados": str(intereses), "total_a_pagar": str(IMPORTE + intereses),
            "tasa_interes": "999",  # el server debe ignorarlo y recalcular con la TNA
            "tasa_interes_id": "", "observaciones": "venta de prueba",
        })
        self.assertTrue(data["success"], data)
        self.assertEqual(data["urlRedirect"], reverse("users:cuentaUser", args=[cliente.pk]))
        return cliente.ventas_nro_cliente.order_by("-id").first()

    def pagar(self, venta, nro_cuota, tipo="total", parcial="", metodo=None):
        return self.post_json(reverse("sales:payCuota"), {
            "cobrador": str(self.cobrador.id), "typePayment": tipo,
            "metodoPago": str((metodo or self.efectivo).id), "ventaID": str(venta.id),
            "cuota": f"Cuota {nro_cuota}", "valorParcial": str(parcial), "moneda": "ars", "tipoCambio": 1400,
        })

    def cuota(self, venta, n):
        venta.refresh_from_db()
        return next(c for c in venta.cuotas if c["cuota"] == f"Cuota {n}")

    def venta_con_3_cuotas_pagas(self, nombre, dni, contrato):
        """Cliente + venta con cuota 0, 1 y 2 pagadas (lo que se suele tener antes de adjudicar)."""
        cliente = self.crear_cliente(nombre, dni)
        venta = self.crear_venta(cliente, contrato)
        for n in (0, 1, 2):
            self.assertTrue(self.pagar(venta, n)["status"])
        return cliente, venta

    def payload_adjudicacion(self, venta, tasa, anticipo=0, porcentaje=50):
        """Replica rellenarCamposDeVenta() de form_create_adju.js."""
        pagado = sum(p.monto for p in PagoCannon.objects.filter(venta=venta).exclude(nro_cuota=0))
        if porcentaje is None:  # sorteo
            base = IMPORTE - pagado
        else:  # negociacion
            base = round(IMPORTE - (pagado * porcentaje / 100 + anticipo))
        intereses = int(base * tasa / 100)
        total = base + intereses
        return {
            "agencia": str(self.sucursal.id), "producto": str(self.producto.id), "tipo_producto": "Moto",
            "nro_contrato": venta.cantidadContratos[0]["nro_contrato"], "modalidad": "Mensual",
            "fecha": HOY, "nro_cuotas": "24", "tasa_interes": str(tasa), "importe": str(IMPORTE),
            "intereses_generados": str(intereses), "total_a_pagar": str(total),
            "importe_x_cuota": str(int(total / 24)), "primer_cuota": str(int(total / 24)),
            "anticipo": str(anticipo),
            "porcentaje_a_reconocer": str(porcentaje or ""), "autorizado_por": self.gerente.nombre,
            "observaciones": "adjudicacion de prueba",
        }

    # ================================================================== FLUJO
    def test_01_alta_cliente(self):
        cliente = self.crear_cliente("juan perez", "40111222")
        self.assertEqual(cliente.nombre, "Juan Perez")
        self.assertTrue(cliente.nro_cliente.startswith("cli_"))
        self.assertEqual(cliente.agencia_registrada, self.sucursal)
        self.assertEqual(self.client.get(reverse("users:cuentaUser", args=[cliente.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("users:list_customers")).status_code, 200)

        # El segundo cliente de la agencia tiene el número siguiente
        otro = self.crear_cliente("ana gomez", "40111333")
        self.assertEqual(int(otro.nro_cliente[4:]), int(cliente.nro_cliente[4:]) + 1)

    def test_02_alta_cliente_validaciones(self):
        self.crear_cliente("juan perez", "40111222")
        url = reverse("users:create_customer")
        base = {"nombre": "Otro Cliente", "dni": "40999888", "tel": "3794123456", "cod_postal": "3450"}

        casos = {
            "dni": {**base, "dni": "40111222"},          # DNI repetido
            "tel": {**base, "tel": "123"},               # teléfono corto
            "nombre": {**base, "nombre": "Juan 123"},    # números en el nombre
            "cod_postal": {**base, "cod_postal": "ABC"},
        }
        for campo, body in casos.items():
            with self.subTest(campo=campo):
                data = self.post_json(url, body)
                self.assertFalse(data["success"])
                self.assertIn(campo, data["errors"])
        self.assertEqual(Cliente.objects.count(), 1)

    def test_03_alta_venta(self):
        cliente = self.crear_cliente("juan perez", "40111222")
        venta = self.crear_venta(cliente)

        self.assertEqual(venta.nro_cliente, cliente)
        self.assertEqual(venta.vendedor, self.vendedor)
        self.assertEqual(venta.supervisor, self.supervisor)
        self.assertEqual(venta.cantidadContratos, [{"nro_contrato": "1000123", "nro_orden": "123"}])
        # tasa: TNA default (70) * 24/12, nunca la que manda el form
        self.assertEqual(venta.tasa_interes, 140.0)
        self.assertEqual(len(venta.cuotas), NRO_CUOTAS + 1)  # cuota 0 + 24

        c0, c1, c2, c14 = (venta.cuotas[i] for i in (0, 1, 2, 14))
        self.assertEqual((c0["total"], c0["bloqueada"]), (ANTICIPO, False))
        self.assertEqual((c1["total"], c1["bloqueada"]), (PRIMER_CUOTA, True))
        self.assertEqual(c2["total"], IMPORTE_X_CUOTA)
        self.assertEqual(c14["total"], int(IMPORTE_X_CUOTA * 1.15))  # 2do año: +15%
        self.assertTrue(c1["fechaDeVencimiento"].startswith("15/"))
        self.assertFalse(venta.adjudicado.get("status"))
        self.assertFalse(venta.deBaja.get("status"))

        self.assertEqual(self.client.get(reverse("sales:detail_sale", args=[venta.pk])).status_code, 200)

    def test_03b_alta_venta_guarda_campos_default(self):
        """CrearVenta llama a setDefaultFields() después del último save(): adjudicado/deBaja quedan en {}."""
        cliente = self.crear_cliente("juan perez", "40111222")
        venta = self.crear_venta(cliente)
        self.assertIn("status", venta.adjudicado)
        self.assertIn("status", venta.deBaja)

    def test_04_alta_venta_validaciones(self):
        cliente = self.crear_cliente("juan perez", "40111222")
        url = reverse("sales:create_sale", args=[cliente.pk])
        data = self.post_json(url, {
            "agencia": "", "producto": "9999", "vendedor": "", "supervisor": str(self.vendedor.id),
            "nro_contrato_1": "12a", "nro_orden_1": "", "fecha": HOY, "nro_cuotas": "24",
        })
        self.assertFalse(data["success"])
        for campo in ("agencia", "producto", "vendedor", "supervisor", "nro_contrato_1", "nro_orden_1"):
            self.assertIn(campo, data["errors"])
        self.assertEqual(Ventas.objects.count(), 0)

    def test_05_cobro_de_cuotas(self):
        cliente = self.crear_cliente("juan perez", "40111222")
        venta = self.crear_venta(cliente)

        # Cuota 1 bloqueada hasta pagar la 0
        data = self.pagar(venta, 1)
        self.assertFalse(data["status"], "no debería poder pagarse la cuota 1 antes que la 0")

        # Sin cobrador -> error controlado
        data = self.post_json(reverse("sales:payCuota"), {
            "cobrador": "", "typePayment": "total", "metodoPago": str(self.efectivo.id),
            "ventaID": str(venta.id), "cuota": "Cuota 0", "moneda": "ars"})
        self.assertFalse(data["status"])

        # Consultar la cuota (modal de pago)
        info = self.post_json(reverse("sales:getCuota"), {"ventaID": venta.id, "cuota": "Cuota 0", "dolar": 1400})
        self.assertEqual(info["total"], ANTICIPO)

        # Cuota 0 total
        data = self.pagar(venta, 0)
        self.assertTrue(data["status"], data)
        self.assertEqual(self.cuota(venta, 0)["status"], "Pagado")
        self.assertFalse(self.cuota(venta, 1)["bloqueada"])
        pago0 = PagoCannon.objects.get(venta=venta, nro_cuota=0)
        self.assertEqual(pago0.monto, ANTICIPO)
        self.assertTrue(pago0.nro_recibo.startswith("RC-"))
        self.assertEqual(pago0.responsable_pago, self.cajero)

        # Cuota 1 en dos pagos parciales (efectivo + transferencia)
        self.assertTrue(self.pagar(venta, 1, "parcial", 50_000)["status"])
        self.assertEqual(self.cuota(venta, 1)["status"], "Parcial")
        self.assertTrue(self.cuota(venta, 2)["bloqueada"])
        self.assertTrue(self.pagar(venta, 1, "parcial", 70_000, self.transferencia)["status"])
        self.assertEqual(self.cuota(venta, 1)["status"], "Pagado")
        self.assertFalse(self.cuota(venta, 2)["bloqueada"])

        # Cuota 2 total; se puede volver a pagar? no.
        self.assertTrue(self.pagar(venta, 2)["status"])
        self.assertFalse(self.pagar(venta, 2)["status"], "una cuota pagada no debería aceptar otro pago")

        self.assertEqual(PagoCannon.objects.filter(venta=venta).count(), 4)
        self.assertEqual(len(PagoCannon.objects.values_list("nro_recibo").distinct()), 4)
        venta.refresh_from_db()
        self.assertEqual(len(venta.cuotas_pagadas()), 2)

        # Detalle, recibo y caja
        self.assertEqual(self.client.get(reverse("sales:detail_sale", args=[venta.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("sales:recibo-preview", args=[pago0.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("sales:caja")).status_code, 200)
        movs = self.client.get(reverse("sales:movs_pagos_list"), {"page_size": 50}).json()
        self.assertEqual(movs["count"], 4, movs)

    def test_06_pago_parcial_mayor_al_resto(self):
        """El server no debería aceptar un parcial que supera lo que falta de la cuota."""
        cliente = self.crear_cliente("juan perez", "40111222")
        venta = self.crear_venta(cliente)
        self.pagar(venta, 0)
        self.assertTrue(self.pagar(venta, 1, "parcial", 100_000)["status"])
        data = self.pagar(venta, 1, "parcial", 100_000)  # la cuota 1 es de 120.000: faltan 20.000
        self.assertFalse(data["status"])
        self.assertIn("$20.000", data["message"])
        cobrado = sum(PagoCannon.objects.filter(venta=venta, nro_cuota=1).values_list("monto", flat=True))
        self.assertLessEqual(cobrado, PRIMER_CUOTA, f"se cobraron ${cobrado} por una cuota de ${PRIMER_CUOTA}")
        # El resto exacto sí se acepta y completa la cuota
        self.assertTrue(self.pagar(venta, 1, "parcial", 20_000)["status"])
        self.assertEqual(self.cuota(venta, 1)["status"], "Pagado")

    def test_07_pago_total_sobre_cuota_parcial(self):
        """'Total' sobre una cuota con un parcial previo debería cobrar solo lo que falta."""
        cliente = self.crear_cliente("juan perez", "40111222")
        venta = self.crear_venta(cliente)
        self.pagar(venta, 0)
        self.pagar(venta, 1, "parcial", 20_000)
        self.pagar(venta, 1, "total")
        cobrado = sum(PagoCannon.objects.filter(venta=venta, nro_cuota=1).values_list("monto", flat=True))
        self.assertEqual(cobrado, PRIMER_CUOTA, f"se cobraron ${cobrado} por una cuota de ${PRIMER_CUOTA}")

    def test_07b_cuota_vencida_con_parcial_abonar_total(self):
        """Una cuota vencida con un parcial figura como 'vencido' y la UI ofrece 'Abonar total':
        tiene que cobrar solo lo que falta."""
        cliente = self.crear_cliente("juan perez", "40111222")
        venta = self.crear_venta(cliente)
        # La venta es de hace 3 meses: la cuota 1 ya venció
        hace_3_meses = (datetime.date.today() - datetime.timedelta(days=90)).strftime("%d/%m/%Y")
        venta.fecha = hace_3_meses + " 00:00"
        venta.crearCuotas()
        venta.testVencimientoCuotas()
        self.pagar(venta, 0)
        self.pagar(venta, 1, "parcial", 20_000)
        self.client.get(reverse("sales:detail_sale", args=[venta.pk]))  # recalcula vencimientos
        info = self.post_json(reverse("sales:getCuota"), {"ventaID": venta.id, "cuota": "Cuota 1", "dolar": 1400})
        self.assertEqual(info["status"], "vencido")
        self.assertTrue(self.pagar(venta, 1, "total")["status"])
        cobrado = sum(PagoCannon.objects.filter(venta=venta, nro_cuota=1).values_list("monto", flat=True))
        self.assertEqual(cobrado, PRIMER_CUOTA)
        self.assertEqual(self.cuota(venta, 1)["status"], "Pagado")

    def test_08_adjudicacion_por_sorteo(self):
        cliente, venta = self.venta_con_3_cuotas_pagas("juan perez", "40111222", "1000123")
        url = reverse("sales:adjSorteo", args=[venta.pk])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["sumaCuotasPagadas"], PRIMER_CUOTA + IMPORTE_X_CUOTA)  # sin la cuota 0
        self.assertEqual(resp.context["tipoDeAdjudicacion"], "SORTEO")

        payload = self.payload_adjudicacion(venta, tasa=100, porcentaje=None)
        data = self.post_json(url, payload)
        self.assertTrue(data["success"], data)
        self.assertEqual(data["urlRedirect"], reverse("users:cuentaUser", args=[cliente.pk]))

        venta.refresh_from_db()
        nueva = cliente.ventas_nro_cliente.exclude(pk=venta.pk).get()

        # Venta original: baja por adjudicación
        self.assertTrue(venta.deBaja["status"])
        self.assertEqual(venta.deBaja["motivo"], "adjudicacion")

        # Venta nueva adjudicada
        self.assertTrue(nueva.adjudicado["status"])
        self.assertEqual(nueva.adjudicado["tipo"], "sorteo")
        self.assertEqual(nueva.adjudicado["contratoAdjudicado"], "1000123")
        self.assertEqual(nueva.nro_operacion, venta.nro_operacion)
        self.assertEqual(len(nueva.cuotas), 24)
        self.assertEqual(nueva.cuotas[0]["cuota"], "Cuota 1")
        self.assertFalse(nueva.cuotas[0]["bloqueada"])
        self.assertEqual(nueva.cuotas[0]["total"], int(payload["importe_x_cuota"]),
                         "la Cuota 1 de la venta adjudicada no puede valer $0")

        # Lo pagado (360.000) se descuenta una sola vez, del importe a financiar: no se acreditan cuotas
        self.assertEqual(nueva.total_a_pagar, (IMPORTE - PRIMER_CUOTA - IMPORTE_X_CUOTA) * 2)  # tasa 100%
        self.assertFalse(PagoCannon.objects.filter(venta=nueva).exists())
        self.assertEqual(self.cuota(nueva, 24)["status"].lower(), "pendiente")
        self.assertEqual(self.cuota(nueva, 1)["status"].lower(), "pendiente")

        # Pantallas y primer cobro de la venta adjudicada
        self.assertEqual(self.client.get(reverse("users:cuentaUser", args=[cliente.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("sales:detail_sale", args=[nueva.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("sales:detail_sale", args=[venta.pk])).status_code, 200)
        data = self.pagar(nueva, 1)
        self.assertTrue(data["status"], data)
        self.assertEqual(self.cuota(nueva, 1)["status"], "Pagado")
        self.assertFalse(self.cuota(nueva, 2)["bloqueada"])

        # Saldo de caja del día: solo el efectivo real (3 cuotas originales + cuota 1 nueva), sin los créditos
        saldo = self.client.get(reverse("sales:arqueoSaldo"), {"agencia_id": self.sucursal.id}).json()
        self.assertEqual(saldo["saldo"], ANTICIPO + PRIMER_CUOTA + IMPORTE_X_CUOTA + int(payload["importe_x_cuota"]))

    def test_09_adjudicacion_por_negociacion(self):
        cliente, venta = self.venta_con_3_cuotas_pagas("maria lopez", "40222333", "2000456")
        url = reverse("sales:adjNegociacion", args=[venta.pk])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["tipoDeAdjudicacion"], "NEGOCIACIÓN")

        payload = self.payload_adjudicacion(venta, tasa=100, anticipo=50_000, porcentaje=50)
        data = self.post_json(url, payload)
        self.assertTrue(data["success"], data)

        venta.refresh_from_db()
        nueva = cliente.ventas_nro_cliente.exclude(pk=venta.pk).get()
        self.assertTrue(venta.deBaja["status"])
        self.assertEqual(venta.deBaja["motivo"], "adjudicacion")
        self.assertTrue(nueva.adjudicado["status"])
        self.assertEqual(nueva.adjudicado["tipo"], "negociacion")
        self.assertEqual(nueva.adjudicado["contratoAdjudicado"], "2000456")
        self.assertEqual(len(nueva.cuotas), 24)
        self.assertEqual(nueva.total_a_pagar, int(payload["total_a_pagar"]))
        self.assertEqual(nueva.cuotas[0]["total"], int(payload["importe_x_cuota"]),
                         "la Cuota 1 de la venta adjudicada no puede valer $0")
        # En negociación no se acredita nada: lo reconocido ya va descontado del total
        self.assertFalse(PagoCannon.objects.filter(venta=nueva).exists())

        self.assertEqual(self.client.get(reverse("sales:detail_sale", args=[nueva.pk])).status_code, 200)
        self.assertTrue(self.pagar(nueva, 1)["status"])
        self.assertEqual(self.cuota(nueva, 1)["status"], "Pagado")

    def _adjudicar_con_error(self, **cambios):
        cliente, venta = self.venta_con_3_cuotas_pagas("juan perez", "40111222", "1000123")
        payload = {**self.payload_adjudicacion(venta, tasa=100, porcentaje=50), **cambios}
        resp = self.client.post(reverse("sales:adjNegociacion", args=[venta.pk]),
                                data=json.dumps(payload), content_type="application/json")
        venta.refresh_from_db()
        self.assertFalse(venta.deBaja.get("status"), "un error no debe dar de baja la venta original")
        self.assertEqual(cliente.ventas_nro_cliente.count(), 1, "un error no debe dejar una venta a medias")
        return resp

    def test_09b_adjudicacion_cuota_1_en_cero(self):
        """Si la administrativa pone la cuota 1 en 0, se respeta (no se cobra)."""
        cliente, venta = self.venta_con_3_cuotas_pagas("maria lopez", "40222333", "2000456")
        payload = {**self.payload_adjudicacion(venta, tasa=100, porcentaje=50), "primer_cuota": "0"}
        self.assertTrue(self.post_json(reverse("sales:adjNegociacion", args=[venta.pk]), payload)["success"])
        nueva = cliente.ventas_nro_cliente.exclude(pk=venta.pk).get()
        self.assertEqual(nueva.cuotas[0]["total"], 0)
        self.assertEqual(nueva.cuotas[1]["total"], int(payload["importe_x_cuota"]))
        # La cuota de $0 se da por abonada y libera la siguiente
        self.assertTrue(self.pagar(nueva, 1)["status"])
        self.assertEqual(self.cuota(nueva, 1)["status"], "Pagado")
        self.assertFalse(self.cuota(nueva, 2)["bloqueada"])

    def test_09c_adjudicacion_sin_cuota_1(self):
        """La cuota 1 es obligatoria: el sistema no la completa solo."""
        resp = self._adjudicar_con_error(primer_cuota="")
        self.assertIn("primer_cuota", resp.json()["errors"])

    def test_10_adjudicacion_importe_invalido(self):
        resp = self._adjudicar_con_error(importe="abc")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["success"])
        self.assertIn("importe", resp.json()["errors"])

    def test_10b_adjudicacion_producto_invalido(self):
        """Un producto/agencia inválido tendría que volver como error del form, no como 500."""
        self.client.raise_request_exception = False
        resp = self._adjudicar_con_error(producto="9999")
        self.assertEqual(resp.status_code, 200, "la vista explota con IntegrityError (500)")
        self.assertIn("producto", resp.json()["errors"])
