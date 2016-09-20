from django.contrib import admin

from pos.models.shift import Shift
from pos.models.stock import Category, Ingredient, Item, ItemIngredient, Order, OrderLine
from pos.models.user import User


class ItemIngreientAdmin(admin.ModelAdmin):
    pass


class CustomerAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    pass


class ItemAdmin(admin.ModelAdmin):
    pass


class OrderLineAdmin(admin.ModelAdmin):
    readonly_fields = ('ingredients', 'item', 'price')


class OrderLineInline(admin.TabularInline):
    readonly_fields = ('item', 'ingredients', 'price')
    model = OrderLine
    extra = 0

    def __unicode__(self):
        return ''

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('customer', 'payment_method', 'message')
    inlines = [OrderLineInline]


class CategoryAdmin(admin.ModelAdmin):
    pass


class ShiftAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, CustomerAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(ItemIngredient, ItemIngreientAdmin)
