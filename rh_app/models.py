from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Employe(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('en_conge', 'En congé'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employe')
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    poste = models.CharField(max_length=50)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    numero_telephone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    adresse = models.TextField(max_length=200)
    date_embauche = models.DateField(default=timezone.now)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Presence(models.Model):
    STATUT_CHOICES = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('en_retard', 'En retard'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField(default=timezone.now)
    heure_entree = models.TimeField()
    heure_sortie = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='present')
    notes = models.TextField(max_length=200, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        ordering = ['-date', 'employe']
        constraints = [
            models.UniqueConstraint(fields=['employe', 'date'], name='unique_presence_per_day')
        ]

    def __str__(self):
        return f"{self.employe} - {self.date}"

class Absence(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('refusee', 'Refusée'),
    ]

    RAISON_CHOICES = [
        ('maladie', 'Maladie'),
        ('personnel', 'Personnel'),
        ('vacances', 'Vacances'),
        ('formation', 'Formation'),
        ('autre', 'Autre'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='absences')
    date_debut = models.DateField()
    date_fin = models.DateField()
    raison = models.CharField(max_length=10, choices=RAISON_CHOICES)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='en_attente')
    description = models.TextField(max_length=200, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
        ordering = ['-date_debut', 'employe']

    def __str__(self):
        return f"{self.employe} - {self.date_debut} au {self.date_fin}"
