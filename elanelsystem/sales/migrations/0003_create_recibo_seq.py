from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_pagocannon_pagocannon_sales_pagoc_venta_i_ee8c3b_idx_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE SEQUENCE IF NOT EXISTS recibo_seq START 1;",
            reverse_sql="DROP SEQUENCE IF EXISTS recibo_seq;"
        ),
    ]