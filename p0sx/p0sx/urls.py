from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from pos.views.foodtracker import active_orders, delivery_screen, delivery_station, production_station, production_station_single, production_station_exclude
from pos.views.littleadmin import (
    AddUserSumupCredit,
    add_credit_stats,
    add_user,
    add_user_credit,
    check_credit,
    check_sumup_status,
    credit_edit,
    credit_overview,
    crew_report,
    fetch_credit_from_ge,
    sale_overview,
    scan_user_card,
    verify_add_credit,
    update_ge_user,
    verify_add_credit_cash
)
from pos.views.shift import AllShiftsViewSet, CurrentShiftViewSet, NewShiftViewSet, ShiftViewSet
from pos.views.stock import (CategoryViewSet,
                             CreditCheckViewSet,
                             DiscountViewSet,
                             ItemViewSet,
                             OrderLineViewSet,
                             OrderViewSet,
                             PurchaseViewSet)
from pos.views.sumup import SumUpAuthView, get_pending_transactions, set_processing, sumup_callback
from pos.views.user import UserViewSet

from pos.views.sso import (
    add_user,
    add_user_callback
)

from rest_framework import routers

sale_url = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('littleadmin:sale'))),
    url(r'overview', sale_overview, name='overview')
]

littleadmin_url = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('littleadmin:overview'))),
    url(r'sumup-init/(?P<instance_id>\d+)/$', SumUpAuthView.as_view(), name='sumup_auth', kwargs={'action': 'init'}),
    url(r'sumup-return/$', SumUpAuthView.as_view(), name='sumup_return', kwargs={'action': 'sumup_return'}),
    url(r'check/', check_credit, name='check'),
    url(r'overview/', credit_overview, name='overview'),
    url(r'edit_crew_credit/(?P<card>\w+)', credit_edit, name='edit_crew_credit'),
    # url(r'sale/', sale_url, name='sale'),
    url(r'sale/', sale_overview, name='sale'),
    url(r'crew_report/', crew_report, name='crew_report'),
    url(r'fetch_from_ge/', fetch_credit_from_ge, name='fetch_credit_from_ge'),
    url(r'scan_user_card', scan_user_card, name='scan_user_card'),
    url(r'add_user_credit/(?P<card>\w+)$', add_user_credit, name='add_user_credit'),
    url(r'add_user_credit/(?P<card>\w+)/sumup$', AddUserSumupCredit.as_view(), name='add_user_credit_sumup'),
    url(r'add_user_credit/(?P<card>\w+)/sumup/(?P<transaction_id>\d+)/verify$', AddUserSumupCredit.as_view(),
        name='add_user_credit_sumup_verify', kwargs={'verify': True}),
    url(r'add_user/(?P<card>\w+)', add_user, name='add_user'),
    url(r'verify_add_credit_cash/(?P<user>\d+)/(?P<amount>\d+)', verify_add_credit_cash, name='verify_add_credit_cash'),
    path('verify_add_credit/<uuid:tid>', verify_add_credit, name='verify_add_credit'),
    # url(r'check_sumup_status/(?P<tid>\[a-zA-Z0-9-]+)', check_sumup_status, name='check_sumup_status'),
    path('check_sumup_status/<uuid:tid>', check_sumup_status, name='check_sumup_status'),
    # url(r'get_pending_transactions/', get_pending_transactions, name='get_pending_transactions'),
    path('get_pending_transactions/', get_pending_transactions, name='get_pending_transactions'),
    # url(r'set_processing/(?P<transaction>\[a-zA-Z0-9-]+)', set_processing, name='set_processing'),
    path('set_processing/<uuid:transaction>', set_processing, name='set_processing'),
    url(r'add_credit_stats', add_credit_stats, name='add_credit_stats'),
    path('update_ge_user/', update_ge_user, name='update_ge_user'),
]

sso_url = [
    path('add_user/', add_user, name='add_user'),
    path('add_user_callback/', add_user_callback, name='add_user_callback')
]

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orderlines', OrderLineViewSet)
router.register(r'items', ItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'current_shift', CurrentShiftViewSet, 'current_shift')
router.register(r'all_shifts', AllShiftsViewSet, 'all_shifts')
router.register(r'create_shift', NewShiftViewSet, 'create_shift')
router.register(r'purchases', PurchaseViewSet, 'purchase')
router.register(r'credit', CreditCheckViewSet, 'credit')
router.register(r'discounts', DiscountViewSet, 'discount')

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('login'))),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='pos/login.djhtml'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/login'), name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'littleadmin/', include((littleadmin_url, "pos"), namespace="littleadmin")),
    url(r'sso/', include((sso_url, "pos"), namespace="sso")),
    # url(r'callback/(?P<tid>\d+)', sumup_callback, name='sumup_callback')
    path('callback/<uuid:tid>', sumup_callback, name='sumup_callback'),
    path('foodtracker/active/', active_orders, name='active_orders'),
    path('foodtracker/production_station/', production_station, name='production_station'),
    path('foodtracker/production_station/<int:category>/', production_station_single, name='production_station_single'),
    path('foodtracker/production_station_exclude/<int:category>/', production_station_exclude, name='production_station_exclude'),
    path('foodtracker/delivery_station/', delivery_station, name='delivery_station'),
    path('foodtracker/delivery_screen/', delivery_screen, name='delivery_screen')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
