from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from pos.views.crew import CrewViewSet
from pos.views.shift import CurrentShiftViewSet, ShiftViewSet
from pos.views.stock import (CategoryViewSet,
                             CreditCheckViewSet,
                             DiscountViewSet,
                             ItemViewSet,
                             OrderLineViewSet,
                             OrderViewSet,
                             PurchaseViewSet)

from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'crew', CrewViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orderlines', OrderLineViewSet)
router.register(r'items', ItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'current_shift', CurrentShiftViewSet,
                base_name='current_shift')
router.register(r'purchases', PurchaseViewSet, 'purchase')
router.register(r'credit', CreditCheckViewSet, 'credit')
router.register(r'discounts', DiscountViewSet, 'discount')
urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
