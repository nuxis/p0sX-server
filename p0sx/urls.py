from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

from pos.views.littleadmin import (add_user,
                                   add_credit_stats,
                                   check_credit,
                                   credit_edit,
                                   credit_overview,
                                   crew_report,
                                   add_user_credit,
                                   sale_overview,
                                   scan_user_card,
                                   fetch_credit_from_ge,
                                   verify_add_credit)
from pos.views.shift import AllShiftsViewSet, CurrentShiftViewSet, NewShiftViewSet, ShiftViewSet
from pos.views.stock import (CategoryViewSet,
                             CreditCheckViewSet,
                             DiscountViewSet,
                             ItemViewSet,
                             OrderLineViewSet,
                             OrderViewSet,
                             PurchaseViewSet)
from pos.views.user import UserViewSet

from rest_framework import routers

sale_url = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('littleadmin:sale:overview'))),
    url(r'overview', sale_overview, name='overview')
]

littleadmin_url = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('littleadmin:overview'))),
    url(r'check/', check_credit, name='check'),
    url(r'overview/', credit_overview, name='overview'),
    url(r'edit_crew_credit/(?P<card>\w+)', credit_edit, name='edit_crew_credit'),
    url(r'sale/', include(sale_url, namespace='sale')),
    url(r'crew_report/', crew_report, name='crew_report'),
    url(r'fetch_from_ge/', fetch_credit_from_ge, name='fetch_credit_from_ge'),
    url(r'scan_user_card', scan_user_card, name='scan_user_card'),
    url(r'add_user_credit/(?P<card>\w+)', add_user_credit, name='add_user_credit'),
    url(r'add_user/(?P<card>\w+)', add_user, name='add_user'),
    url(r'verify_add_credit/(?P<user>\d+)/(?P<amount>\d+)', verify_add_credit, name='verify_add_credit'),
    url(r'add_credit_stats', add_credit_stats, name='add_credit_stats')
]

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
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
    url(r'^login/$', auth_views.login, {'template_name': 'pos/login.djhtml'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'littleadmin/', include(littleadmin_url, namespace='littleadmin'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
