from django.contrib import admin

from pos.models.shift import Shift
from pos.models.stock import Category, Discount, FoodLog, Ingredient, Item, ItemIngredient, Order, OrderLine
from pos.models.sumup import SumUpAPIKey, SumUpCard, SumUpTerminal, SumUpTransaction
from pos.models.user import CreditUpdate, User, GeekeventsToken


class CreditUpdateAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp', 'amount', 'user', 'updated_by_user', 'geekevents_id')
    pass


class DiscountAdmin(admin.ModelAdmin):
    pass


class ItemIngredientAdmin(admin.ModelAdmin):
    pass


class GeekeventsTokenInline(admin.StackedInline):
    readonly_fields = ('ge_user_id', 'timestamp', 'token')
    model = GeekeventsToken
    extra = 0

    def __unicode__(self):
        return self.token

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class UserAdmin(admin.ModelAdmin):
    search_fields = ('card', 'first_name', 'last_name',)
    list_display = ('full_name', 'credit',)
    inlines = [GeekeventsTokenInline]

    def get_inline_instances(self, request, obj=None):
        if not obj or not hasattr(obj, 'geekeventstoken'):
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)

    def full_name(self, obj):
        if hasattr(obj, 'geekeventstoken'):
            return '{} {} via Geekevents SSO'.format(obj.first_name, obj.last_name)
        return '{} {}'.format(obj.first_name, obj.last_name)

    pass


class IngredientAdmin(admin.ModelAdmin):
    pass


class ItemAdmin(admin.ModelAdmin):
    pass


class OrderLineAdmin(admin.ModelAdmin):
    readonly_fields = ('ingredients', 'item', 'price')
    list_display = ('item', 'order', 'state')


class OrderLineInline(admin.TabularInline):
    readonly_fields = ('item', 'ingredients', 'price')
    model = OrderLine
    extra = 0

    def __unicode__(self):
        return ''

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class CategoryAdmin(admin.ModelAdmin):
    pass


class ShiftAdmin(admin.ModelAdmin):
    pass


class SumUpAPIKeyAdmin(admin.ModelAdmin):
    pass


class SumUpTerminalAdmin(admin.ModelAdmin):
    pass


class SumUpTransactionAdmin(admin.ModelAdmin):
    pass


class SumUpCardAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created', 'timestamp')
    ordering = ('-created',)
    list_display = ('user', 'amount', 'status', 'created', 'transaction_id', 'transaction_comment',)
    pass


class FoodLogAdmin(admin.ModelAdmin):
    readonly_fields = ('orderline', 'state', 'timestamp')
    list_display = ('orderline_id', 'orderline', 'timestamp', 'state')
    pass


class FoodLogInline(admin.TabularInline):
    readonly_fields = ('orderline', 'state', 'timestamp')
    model = FoodLog
    extra = 0

    def __unicode__(self):
        return ''

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'payment_method', 'cashier', 'authenticated_user')
    list_display = ('id', 'user', 'date', 'sum', 'state')
    inlines = [OrderLineInline]


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(ItemIngredient, ItemIngredientAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(CreditUpdate, CreditUpdateAdmin)

admin.site.register(SumUpAPIKey, SumUpAPIKeyAdmin)
admin.site.register(SumUpTerminal, SumUpTerminalAdmin)
admin.site.register(SumUpTransaction, SumUpTransactionAdmin)
admin.site.register(SumUpCard, SumUpCardAdmin)

admin.site.register(FoodLog, FoodLogAdmin)
