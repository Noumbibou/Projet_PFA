from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, date, timedelta
import csv
from reportlab.pdfgen import canvas
from io import BytesIO
import json

from .models import Employe, Presence, Absence
from .forms import (
    UserRegistrationForm, EmployeForm, PresenceForm, AbsenceForm,
    PresenceFilterForm, AbsenceFilterForm
)

def is_admin(user):
    return user.is_staff

def is_staff(user):
    return user.is_staff

@login_required
def dashboard(request):
    if request.user.is_staff:
        # Statistiques pour l'admin
        total_employes = Employe.objects.count()
        presences_aujourdhui = Presence.objects.filter(date=timezone.now().date()).count()
        absences_en_attente = Absence.objects.filter(statut='en_attente').count()
        
        # Calcul du taux de présence (sur les 30 derniers jours)
        date_limite = timezone.now().date() - timedelta(days=30)
        total_jours = 30 * total_employes
        presences_total = Presence.objects.filter(date__gte=date_limite).count()
        taux_presence = round((presences_total / total_jours) * 100) if total_jours > 0 else 0

        # Données pour le graphique des présences par mois
        mois_labels = []
        presences_data = []
        for i in range(6):  # 6 derniers mois
            date = timezone.now().date() - timedelta(days=30*i)
            mois_labels.insert(0, date.strftime('%B %Y'))
            presences = Presence.objects.filter(
                date__year=date.year,
                date__month=date.month
            ).count()
            presences_data.insert(0, presences)

        # Statistiques des absences
        absences_stats = [
            Absence.objects.filter(statut='approuvee').count(),
            Absence.objects.filter(statut='en_attente').count(),
            Absence.objects.filter(statut='refusee').count()
        ]

        context = {
            'total_employes': total_employes,
            'presences_aujourdhui': presences_aujourdhui,
            'absences_en_attente': absences_en_attente,
            'taux_presence': taux_presence,
            'mois_labels': json.dumps(mois_labels),
            'presences_data': json.dumps(presences_data),
            'absences_stats': json.dumps(absences_stats)
        }
    else:
        # Données pour l'employé
        employe = request.user.employe
        dernieres_presences = Presence.objects.filter(
            employe=employe
        ).order_by('-date')[:5]
        
        dernieres_absences = Absence.objects.filter(
            employe=employe
        ).order_by('-date_debut')[:5]

        context = {
            'dernieres_presences': dernieres_presences,
            'dernieres_absences': dernieres_absences
        }

    return render(request, 'rh_app/dashboard.html', context)

class EmployeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Employe
    template_name = 'rh_app/employe_list.html'
    context_object_name = 'employes'
    
    def test_func(self):
        return self.request.user.is_staff

class EmployeDetailView(LoginRequiredMixin, DetailView):
    model = Employe
    template_name = 'rh_app/employe_detail.html'
    context_object_name = 'employe'
    
    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        return self.request.user.employe

class EmployeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'rh_app/employe_form.html'
    success_url = reverse_lazy('employe_list')
    
    def test_func(self):
        return self.request.user.is_staff

class EmployeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'rh_app/employe_form.html'
    success_url = reverse_lazy('employe_list')
    
    def test_func(self):
        return self.request.user.is_staff

class EmployeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employe
    template_name = 'rh_app/employe_confirm_delete.html'
    success_url = reverse_lazy('employe_list')
    
    def test_func(self):
        return self.request.user.is_staff

@login_required
@user_passes_test(is_staff)
def employe_list(request):
    employes = Employe.objects.all()
    return render(request, 'rh_app/employe_list.html', {'employes': employes})

@login_required
@user_passes_test(is_staff)
def employe_detail(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    return render(request, 'rh_app/employe_detail.html', {'employe': employe})

@login_required
@user_passes_test(is_staff)
def employe_create(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            employe = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'employe': {
                        'id': employe.id,
                        'nom': employe.nom,
                        'prenom': employe.prenom,
                        'poste': employe.poste,
                        'email': employe.email,
                        'numero_telephone': employe.numero_telephone,
                    }
                })
            messages.success(request, 'Employé créé avec succès.')
            return redirect('rh_app:employe_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': form.errors.as_text()
                })
    else:
        form = EmployeForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'error': 'Méthode non autorisée'
        })
    
    return render(request, 'rh_app/employe_form.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def employe_update(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employé mis à jour avec succès.')
            return redirect('rh_app:employe_list')
    else:
        form = EmployeForm(instance=employe)
    return render(request, 'rh_app/employe_form.html', {'form': form, 'employe': employe})

@login_required
@user_passes_test(is_staff)
def employe_delete(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        employe.delete()
        messages.success(request, 'Employé supprimé avec succès.')
        return redirect('rh_app:employe_list')
    return render(request, 'rh_app/employe_confirm_delete.html', {'employe': employe})

@login_required
def presence_list(request):
    if request.user.is_staff:
        presences = Presence.objects.all()
    else:
        presences = Presence.objects.filter(employe=request.user.employe)
    
    # Filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    employe_id = request.GET.get('employe')
    statut = request.GET.get('statut')

    if date_debut:
        presences = presences.filter(date__gte=date_debut)
    if date_fin:
        presences = presences.filter(date__lte=date_fin)
    if employe_id and request.user.is_staff:
        presences = presences.filter(employe_id=employe_id)
    if statut:
        presences = presences.filter(statut=statut)

    return render(request, 'rh_app/presence_list.html', {
        'presences': presences,
        'employes': Employe.objects.all() if request.user.is_staff else None
    })

@login_required
def presence_create(request):
    if request.method == 'POST':
        form = PresenceForm(request.POST, user=request.user)
        if form.is_valid():
            presence = form.save(commit=False)
            if not request.user.is_staff:
                presence.employe = request.user.employe
            presence.save()
            messages.success(request, 'Présence enregistrée avec succès.')
            return redirect('rh_app:presence_list')
    else:
        form = PresenceForm(user=request.user)
    return render(request, 'rh_app/presence_form.html', {'form': form})

@login_required
def presence_update(request, pk):
    presence = get_object_or_404(Presence, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_staff and presence.employe != request.user.employe:
        messages.error(request, "Vous n'avez pas la permission de modifier cette présence.")
        return redirect('rh_app:presence_list')
    
    if request.method == 'POST':
        form = PresenceForm(request.POST, instance=presence, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Présence modifiée avec succès.')
            return redirect('rh_app:presence_list')
    else:
        form = PresenceForm(instance=presence, user=request.user)
    
    return render(request, 'rh_app/presence_form.html', {'form': form, 'presence': presence})

@login_required
def presence_export_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'exporter les données.")
        return redirect('rh_app:presence_list')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="presences.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Employé', 'Heure Entrée', 'Heure Sortie', 'Statut'])

    presences = Presence.objects.all()
    for presence in presences:
        writer.writerow([
            presence.date,
            f"{presence.employe.nom} {presence.employe.prenom}",
            presence.heure_entree,
            presence.heure_sortie,
            presence.get_statut_display()
        ])

    return response

@login_required
def absence_list(request):
    if request.user.is_staff:
        absences = Absence.objects.all()
    else:
        absences = Absence.objects.filter(employe=request.user.employe)
    
    # Filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    employe_id = request.GET.get('employe')
    statut = request.GET.get('statut')

    if date_debut:
        absences = absences.filter(date_debut__gte=date_debut)
    if date_fin:
        absences = absences.filter(date_fin__lte=date_fin)
    if employe_id and request.user.is_staff:
        absences = absences.filter(employe_id=employe_id)
    if statut:
        absences = absences.filter(statut=statut)

    return render(request, 'rh_app/absence_list.html', {
        'absences': absences,
        'employes': Employe.objects.all() if request.user.is_staff else None
    })

@login_required
def absence_create(request):
    if request.method == 'POST':
        form = AbsenceForm(request.POST, user=request.user)
        if form.is_valid():
            absence = form.save(commit=False)
            if not request.user.is_staff:
                absence.employe = request.user.employe
            absence.save()
            messages.success(request, 'Demande d\'absence enregistrée avec succès.')
            return redirect('rh_app:absence_list')
    else:
        form = AbsenceForm(user=request.user)
    return render(request, 'rh_app/absence_form.html', {'form': form})

@login_required
def absence_update(request, pk):
    absence = get_object_or_404(Absence, pk=pk)
    if not request.user.is_staff and absence.employe != request.user.employe:
        messages.error(request, "Vous n'avez pas la permission de modifier cette absence.")
        return redirect('rh_app:absence_list')
    
    if request.method == 'POST':
        form = AbsenceForm(request.POST, instance=absence, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absence mise à jour avec succès.')
            return redirect('rh_app:absence_list')
    else:
        form = AbsenceForm(instance=absence, user=request.user)
    return render(request, 'rh_app/absence_form.html', {'form': form, 'absence': absence})

@login_required
def absence_export_pdf(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'exporter les données.")
        return redirect('rh_app:absence_list')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="absences.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # En-tête
    p.drawString(100, 800, "Liste des Absences")
    p.drawString(100, 780, f"Date d'export: {timezone.now().strftime('%d/%m/%Y')}")

    # En-tête du tableau
    y = 750
    p.drawString(100, y, "Date Début")
    p.drawString(200, y, "Date Fin")
    p.drawString(300, y, "Employé")
    p.drawString(400, y, "Raison")
    p.drawString(500, y, "Statut")

    # Données
    absences = Absence.objects.all()
    for absence in absences:
        y -= 20
        if y < 50:  # Nouvelle page si nécessaire
            p.showPage()
            y = 750
            # Réécrire l'en-tête
            p.drawString(100, y, "Date Début")
            p.drawString(200, y, "Date Fin")
            p.drawString(300, y, "Employé")
            p.drawString(400, y, "Raison")
            p.drawString(500, y, "Statut")
            y -= 20

        p.drawString(100, y, absence.date_debut.strftime('%d/%m/%Y'))
        p.drawString(200, y, absence.date_fin.strftime('%d/%m/%Y'))
        p.drawString(300, y, f"{absence.employe.nom} {absence.employe.prenom}")
        p.drawString(400, y, absence.get_raison_display())
        p.drawString(500, y, absence.get_statut_display())

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response
