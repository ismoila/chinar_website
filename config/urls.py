from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from products.payments import payme_callback, click_prepare, click_complete
from pages.sitemaps import SITEMAPLAR

urlpatterns = [
    path('admin/', admin.site.urls),
    # To'lov callback'lari — til prefiksisiz bo'lishi SHART
    path('payments/payme/', payme_callback),
    path('payments/click/prepare/', click_prepare),
    path('payments/click/complete/', click_complete),
    # SEO: qidiruv tizimlari uchun
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPLAR}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
] + i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('pages.urls', namespace='pages')),
    path('', include('products.urls', namespace='products')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('nested_admin/', include('nested_admin.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)