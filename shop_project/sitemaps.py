from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product  # ← Make sure this import is correct

# Static Pages Sitemap
class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return ['home', 'shop', 'subscribe']

    def location(self, item):
        return reverse(item)

# Products Sitemap (Dynamic)
class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)  # Adjust filter if your field name is different

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('product_detail', args=[obj.id])
