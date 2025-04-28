from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'rh_app'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='rh_app/login.html',
        redirect_authenticated_user=True,
        next_page='rh_app:dashboard'
    ), name='login'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='rh_app/logout.html',
        next_page='rh_app:login'
    ), name='logout'),
    
    # Employés
    path('employes/', login_required(views.employe_list), name='employe_list'),
    path('employes/<int:pk>/', login_required(views.employe_detail), name='employe_detail'),
    path('employes/nouveau/', login_required(views.employe_create), name='employe_create'),
    path('employes/<int:pk>/modifier/', login_required(views.employe_update), name='employe_update'),
    path('employes/<int:pk>/supprimer/', login_required(views.employe_delete), name='employe_delete'),
    
    # Présences
    path('presences/', login_required(views.presence_list), name='presence_list'),
    path('presences/nouvelle/', login_required(views.presence_create), name='presence_create'),
    path('presences/<int:pk>/modifier/', login_required(views.presence_update), name='presence_update'),
    path('presences/export/csv/', login_required(views.presence_export_csv), name='presence_export_csv'),
    
    # Absences
    path('absences/', login_required(views.absence_list), name='absence_list'),
    path('absences/nouvelle/', login_required(views.absence_create), name='absence_create'),
    path('absences/<int:pk>/modifier/', login_required(views.absence_update), name='absence_update'),
    path('absences/export/pdf/', login_required(views.absence_export_pdf), name='absence_export_pdf'),
] 