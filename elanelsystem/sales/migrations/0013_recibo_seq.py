from django.db import migrations


class Migration(migrations.Migration):
    """PagoCannon.save() numera los recibos con nextval('recibo_seq'), pero ninguna migración
    creaba la secuencia: en una base nueva el primer cobro fallaba. IF NOT EXISTS la deja
    intacta en las bases donde ya se creó a mano."""

    dependencies = [
        ("sales", "0012_cuentacobranza_activo"),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE SEQUENCE IF NOT EXISTS recibo_seq",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
