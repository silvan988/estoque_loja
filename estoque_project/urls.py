# estoque_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importar settings
from django.conf.urls.static import static # Importar static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('estoque/', include('produtos.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('api/', include('produtos.api_urls')),
    path('', include('produtos.urls')),
]

# --- ADICIONE ESTE BLOCO ---
# Serve arquivos estáticos e de mídia APENAS em modo de desenvolvimento (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Opcional: Para servir STATIC_ROOT também em desenvolvimento, se necessário
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# --- FIM DO BLOCO ADICIONAL ---