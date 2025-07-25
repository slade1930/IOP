# Generated by Django 5.2.2 on 2025-06-15 16:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metodos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemaSimplex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objetivo', models.CharField(help_text='Función objetivo, ej: 3x1 + 2x2 + 5x3', max_length=255)),
                ('tipo_optimizacion', models.CharField(choices=[('maximizar', 'Maximizar'), ('minimizar', 'Minimizar')], default='maximizar', help_text='Seleccione si desea maximizar o minimizar la función objetivo', max_length=10)),
                ('restricciones', models.TextField(help_text='Ingrese las restricciones separadas por punto y coma. Ej: 2x1 + x2 <= 20; x1 + 3x2 <= 30')),
                ('variables_decision', models.PositiveIntegerField(default=2, help_text='Número de variables de decisión')),
                ('variables_holgura', models.PositiveIntegerField(default=0, help_text='Número de variables de holgura (se calcula automáticamente)')),
                ('tolerancia', models.FloatField(default=0.001, help_text='Tolerancia para considerar cero')),
                ('max_iteraciones', models.IntegerField(default=100, help_text='Número máximo de iteraciones')),
                ('tabla_inicial', models.TextField(blank=True, help_text='Tabla inicial del simplex en formato JSON', null=True)),
                ('tabla_final', models.TextField(blank=True, help_text='Tabla final del simplex en formato JSON', null=True)),
                ('solucion', models.TextField(blank=True, help_text='Solución óptima encontrada', null=True)),
                ('grafico_base64', models.TextField(blank=True, help_text='Gráfico de la región factible (para problemas 2D)', null=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Problema de Programación Lineal',
                'verbose_name_plural': 'Problemas de Programación Lineal',
                'ordering': ['-creado'],
            },
        ),
        migrations.DeleteModel(
            name='Simplex',
        ),
    ]
