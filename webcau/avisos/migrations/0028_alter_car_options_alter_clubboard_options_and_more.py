# Generated by Django 4.0.3 on 2023-05-25 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avisos', '0027_alter_member_rut'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='car',
            options={'ordering': ['member', 'alias'], 'verbose_name': 'Vehículo', 'verbose_name_plural': 'Vehículos'},
        ),
        migrations.AlterModelOptions(
            name='clubboard',
            options={'ordering': ['name'], 'verbose_name': 'Directiva', 'verbose_name_plural': 'Directivas'},
        ),
        migrations.AlterModelOptions(
            name='clubboardmember',
            options={'ordering': ['clubboard', 'position'], 'verbose_name': 'Miembro de la directiva', 'verbose_name_plural': 'Miembros de la directiva'},
        ),
        migrations.AlterModelOptions(
            name='emergencycontact',
            options={'ordering': ['member', 'name'], 'verbose_name': 'Contacto de emergencia', 'verbose_name_plural': 'Contactos de emergencia'},
        ),
        migrations.AlterModelOptions(
            name='friend',
            options={'ordering': ['name', 'first_surname'], 'verbose_name': 'Amigo', 'verbose_name_plural': 'Amigos'},
        ),
        migrations.AlterModelOptions(
            name='globalsettings',
            options={'verbose_name': 'Configuración global', 'verbose_name_plural': 'Configuración global'},
        ),
        migrations.AlterModelOptions(
            name='medicalrecord',
            options={'ordering': ['member'], 'verbose_name': 'Ficha médica', 'verbose_name_plural': 'Fichas médicas'},
        ),
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['name', 'first_surname'], 'verbose_name': 'Socio', 'verbose_name_plural': 'Socios'},
        ),
        migrations.AlterModelOptions(
            name='noticecategory',
            options={'ordering': ['priority'], 'verbose_name': 'Categoría de aviso', 'verbose_name_plural': 'Categorías de avisos'},
        ),
        migrations.AlterModelOptions(
            name='shortnotice',
            options={'ordering': ['-start_date'], 'verbose_name': 'Aviso Rápido', 'verbose_name_plural': 'Avisos Rápidos'},
        ),
        migrations.AlterField(
            model_name='member',
            name='rut',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
