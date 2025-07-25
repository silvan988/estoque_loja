# Generated by Django 5.2.4 on 2025-07-26 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0005_alter_movimentacaoestoque_tipo_movimentacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='unidade_medida',
            field=models.CharField(choices=[('unidade(s)', 'Unidade(s)'), ('kg(s)', 'Quilograma(s) (kg)'), ('litro(s)', 'Litro(s) (L)'), ('metro(s)', 'Metro(s) (m)'), ('pacote(s)', 'Pacote(s)'), ('caixa(s)', 'Caixa(s)'), ('par(es)', 'Par(es)'), ('rolo(s)', 'Rolo(s)'), ('conjunto(s)', 'Conjunto(s)'), ('galão(ões)', 'Galão(ões)'), ('saco(s)', 'Saco(s)')], default='unidade', max_length=50, verbose_name='Unidade de Medida'),
        ),
    ]
