
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from main import views

urlpatterns = [
    path("", view=views.dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),
    path('cahier_de_texte/', include('cahier_de_texte.urls')),
    path('maquette/', include('maquette.urls')),
    path('paiement/', include('paiement.urls')),
    path('import_data/', include('import_data.urls')),
    path('conges/', include('conges.urls')),
    path('planning/', include('planning.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
