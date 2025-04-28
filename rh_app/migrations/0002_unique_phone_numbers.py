from django.db import migrations, models
from django.db.models import Count

def make_phone_numbers_unique(apps, schema_editor):
    Employe = apps.get_model('rh_app', 'Employe')
    # Trouver les numéros de téléphone en double
    duplicates = (
        Employe.objects.values('numero_telephone')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    # Pour chaque numéro de téléphone en double
    for duplicate in duplicates:
        phone = duplicate['numero_telephone']
        # Obtenir tous les employés avec ce numéro
        employes = Employe.objects.filter(numero_telephone=phone).order_by('id')
        # Garder le premier inchangé, modifier les autres
        for i, employe in enumerate(employes[1:], 1):
            # Ajouter un suffixe au numéro de téléphone
            employe.numero_telephone = f"{phone}_{i}"
            employe.save()

class Migration(migrations.Migration):

    dependencies = [
        ('rh_app', '0001_initial'),
    ]

    operations = [
        # D'abord, exécuter la fonction pour rendre les numéros uniques
        migrations.RunPython(make_phone_numbers_unique),
        
        # Ensuite, ajouter la contrainte d'unicité
        migrations.AlterField(
            model_name='employe',
            name='numero_telephone',
            field=models.CharField(max_length=15, unique=True),
        ),
    ] 