from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Employe, Presence, Absence

class EmployeInline(admin.StackedInline):
    model = Employe
    can_delete = False
    verbose_name_plural = 'Employé'

class CustomUserAdmin(UserAdmin):
    inlines = (EmployeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_employe_status')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def get_employe_status(self, obj):
        try:
            return obj.employe.statut
        except:
            return "Non défini"
    get_employe_status.short_description = 'Statut'

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'poste', 'statut', 'email', 'numero_telephone')
    list_filter = ('statut', 'poste')
    search_fields = ('nom', 'prenom', 'email', 'numero_telephone')
    ordering = ('nom', 'prenom')

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('employe', 'date', 'heure_entree', 'heure_sortie', 'statut')
    list_filter = ('date', 'statut', 'employe')
    search_fields = ('employe__nom', 'employe__prenom')
    date_hierarchy = 'date'

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('employe', 'date_debut', 'date_fin', 'raison', 'statut')
    list_filter = ('statut', 'raison', 'date_debut', 'date_fin')
    search_fields = ('employe__nom', 'employe__prenom', 'description')
    date_hierarchy = 'date_debut'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
