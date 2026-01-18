import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Carga datos iniciales para desarrollo/Docker (idempotente)."

    def handle(self, *args, **options):
        # Imports "tardíos" para que Django ya esté configurado
        from users.models import Sucursal, Usuario, Cliente
        from configuracion.models import Configuracion
        from liquidacion.models import MontoTardanzaAusencia, Asegurado
        from products.models import Plan, Products
        from sales.models import MetodoPago, CuentaCobranza, CoeficientesListadePrecios

        # -----------------------------
        # 1) Sucursal base
        # -----------------------------
        direccion_raw = os.getenv("DEFAULT_SUCURSAL_DIRECCION", "Av. Demo 123")
        hora_apertura = os.getenv("DEFAULT_SUCURSAL_HORA_APERTURA", "08:00")
        provincia_raw = os.getenv("DEFAULT_SUCURSAL_PROVINCIA", "Corrientes")
        localidad_raw = os.getenv("DEFAULT_SUCURSAL_LOCALIDAD", "Corrientes")

        # Normalizamos igual que el save() del modelo para que sea realmente idempotente
        direccion = direccion_raw.capitalize()
        provincia = provincia_raw.title()
        localidad = localidad_raw.title()

        sucursal = (
            Sucursal.objects.filter(
                direccion=direccion,
                provincia__iexact=provincia,
                localidad__iexact=localidad,
            ).first()
        )
        if not sucursal:
            sucursal = Sucursal.objects.create(
                direccion=direccion,
                hora_apertura=hora_apertura,
                provincia=provincia,
                localidad=localidad,
                sucursal_central=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Sucursal creada: {sucursal}"))
        else:
            self.stdout.write(self.style.NOTICE(f"Sucursal existente: {sucursal}"))

        # -----------------------------
        # 2) Usuario admin inicial
        # -----------------------------
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@local.test").lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin1234")
        nombre = os.getenv("DJANGO_SUPERUSER_NAME", "Admin Local")
        dni = os.getenv("DJANGO_SUPERUSER_DNI", "00000000")
        rango = os.getenv("DJANGO_SUPERUSER_RANGO", "Admin")
        c_value = os.getenv("DJANGO_SUPERUSER_C", password)

        user = Usuario.objects.filter(email=email).first()
        if not user:
            user = Usuario(
                email=email,
                nombre=nombre,
                dni=dni,
                rango=rango,
                c=c_value,
                fec_ingreso="01/01/2025",
                is_active=True,
                is_staff=True,
                is_superuser=True,
            )
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Usuario admin creado: {user.email}"))
        else:
            # Mantenemos el user, pero sincronizamos campos clave para que sea usable
            changed = False
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                changed = True
            if user.nombre != nombre:
                user.nombre = nombre
                changed = True
            if user.dni != dni:
                user.dni = dni
                changed = True
            if user.rango != rango:
                user.rango = rango
                changed = True
            if not user.c:
                user.c = c_value
                changed = True
            # Siempre seteamos password para que el login sea predecible en Docker
            user.set_password(password)
            changed = True
            if changed:
                user.save()
            self.stdout.write(self.style.NOTICE(f"Usuario admin existente (actualizado): {user.email}"))

        # Linkeos con sucursal
        try:
            user.sucursales.add(sucursal)
        except Exception:
            pass
        if sucursal.gerente_id != user.id:
            sucursal.gerente = user
            sucursal.save()

        # -----------------------------
        # 3) Configuración básica
        # -----------------------------
        Configuracion.objects.get_or_create(clave="app_name", defaults={"valor": "ElanelSystem"})
        Configuracion.objects.get_or_create(clave="seeded", defaults={"valor": "true"})

        # -----------------------------
        # 4) Tablas auxiliares (métodos de pago / cuentas)
        # -----------------------------
        for alias in ["Efectivo", "Transferencia", "Tarjeta", "Banco", "Mercado Pago"]:
            # El modelo guarda alias con .capitalize()
            normalized = alias.capitalize()
            MetodoPago.objects.get_or_create(alias=normalized)

        for alias in ["Caja Central", "Cuenta Banco", "Caja Sucursal"]:
            normalized = alias.capitalize()
            CuentaCobranza.objects.get_or_create(alias=normalized)

        # -----------------------------
        # 5) Liquidación: instancia única + asegurado default
        # -----------------------------
        MontoTardanzaAusencia.get_solo()
        Asegurado.objects.get_or_create(dinero=0, dirigido="N/A")

        # -----------------------------
        # 6) Productos / planes demo
        # -----------------------------
        planes_demo = [
            # valor_nominal, suscripcion/primer_cuota, porcentajes
            (150000, 7000, 0.008, 0.02, 0.088, 0.08),
            (300000, 13000, -0.008, 0.02, 0.088, 0.08),
            (500000, 22000, 0.0032, 0.0333, 0.088, 0.08),
        ]

        created_plans = 0
        for (valor_nominal, sus, c24, c30, c48, c60) in planes_demo:
            plan = Plan.objects.filter(valor_nominal=valor_nominal).first()
            if not plan:
                plan = Plan.objects.create(
                    valor_nominal=valor_nominal,
                    suscripcion=sus,
                    primer_cuota=sus,
                    c24_porcentage=c24,
                    c30_porcentage=c30,
                    c48_porcentage=c48,
                    c60_porcentage=c60,
                )
                created_plans += 1
            else:
                # actualiza por si cambiaron valores
                plan.suscripcion = sus
                plan.primer_cuota = sus
                plan.c24_porcentage = c24
                plan.c30_porcentage = c30
                plan.c48_porcentage = c48
                plan.c60_porcentage = c60
                plan.save()

        if created_plans:
            self.stdout.write(self.style.SUCCESS(f"Planes creados: {created_plans}"))

        # Productos demo (idempotente por nombre)
        def ensure_product(nombre: str, tipodePlan: str, tipo_de_producto: str, plan_valor: int | None):
            qs = Products.objects.filter(nombre=nombre)
            obj = qs.first()
            plan_obj = Plan.objects.filter(valor_nominal=plan_valor).first() if plan_valor else None
            if not obj:
                Products.objects.create(
                    nombre=nombre,
                    tipodePlan=tipodePlan,
                    tipo_de_producto=tipo_de_producto,
                    plan=plan_obj,
                    activo=True,
                )
            else:
                obj.tipodePlan = tipodePlan
                obj.tipo_de_producto = tipo_de_producto
                obj.plan = plan_obj
                obj.activo = True
                obj.save()

        ensure_product("Solución Base", "Base", "Solucion", 150000)
        ensure_product("Combo Estándar", "Estandar", "Combo", 300000)
        ensure_product("Moto Premium", "Premium", "Moto", 500000)

        # -----------------------------
        # 7) Cliente demo (para probar flujos)
        # -----------------------------
        if not Cliente.objects.filter(dni="12345678").exists():
            Cliente.objects.create(
                nro_cliente="",  # se asigna automáticamente (cli_###) por sucursal
                nombre="Cliente Demo",
                dni="12345678",
                tel="3794123456",
                domic="Calle Falsa 123",
                loc=localidad,
                prov=provincia,
                cod_postal="3400",
                agencia_registrada=sucursal,
            )

        # -----------------------------
        # 8) Coeficientes de lista de precios (mínimos)
        # -----------------------------
        coef_demo = [
            # (valor_nominal, cuota, porcentaje)
            (150000, 24, 0.008),
            (150000, 30, 0.02),
            (300000, 24, -0.008),
            (300000, 30, 0.02),
            (500000, 24, 0.0032),
            (500000, 30, 0.0333),
        ]
        for vn, cuota, pct in coef_demo:
            obj = CoeficientesListadePrecios.objects.filter(valor_nominal=vn, cuota=cuota).first()
            if not obj:
                CoeficientesListadePrecios.objects.create(
                    valor_nominal=vn,
                    cuota=cuota,
                    porcentage=pct,
                )
            else:
                if obj.porcentage != pct:
                    obj.porcentage = pct
                    obj.save()

        self.stdout.write(self.style.SUCCESS("Seed completo ✅"))