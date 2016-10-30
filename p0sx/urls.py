from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from pos.views.crew import CrewViewSet
from pos.views.littleadmin import check_credit, credit_edit, credit_overview, sale_overview, crew_report
from pos.views.shift import AllShiftsViewSet, CurrentShiftViewSet, NewShiftViewSet, ShiftViewSet
from pos.views.stock import (CategoryViewSet,
                             CreditCheckViewSet,
                             DiscountViewSet,
                             ItemViewSet,
                             OrderLineViewSet,
                             OrderViewSet,
                             PurchaseViewSet)


from rest_framework import routers

sale_url = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('littleadmin:sale:overview'))),
    url(r'overview', sale_overview, name='overview')
]

littleadmin_url = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('littleadmin:overview'))),
    url(r'check/', check_credit, name='check'),
    url(r'overview/', credit_overview, name='overview'),
    url(r'edit/(?P<card>\w+)', credit_edit, name='edit'),
    url(r'sale/', include(sale_url, namespace='sale')),
    url(r'crew_report/', crew_report, name="crew_report")
]

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
router.register(r'all_shifts', AllShiftsViewSet,
                base_name='all_shifts')
router.register(r'create_shift', NewShiftViewSet, base_name='create_shift')
router.register(r'purchases', PurchaseViewSet, 'purchase')
router.register(r'credit', CreditCheckViewSet, 'credit')
router.register(r'discounts', DiscountViewSet, 'discount')
urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'littleadmin/', include(littleadmin_url, namespace='littleadmin'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
