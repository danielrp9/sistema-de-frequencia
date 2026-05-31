# Generated to align Presenca migrations with the current model.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presence_service', '0003_alter_presenca_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='presenca',
            old_name='data_registro',
            new_name='horario_registro',
        ),
        migrations.AlterField(
            model_name='presenca',
            name='ip_registrado',
            field=models.GenericIPAddressField(),
        ),
        migrations.AlterField(
            model_name='presenca',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='presenca',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AddField(
            model_name='presenca',
            name='status',
            field=models.CharField(
                choices=[('VALIDA', 'Válida'), ('INVALIDA', 'Inválida')],
                default='VALIDA',
                max_length=20,
            ),
        ),
    ]
