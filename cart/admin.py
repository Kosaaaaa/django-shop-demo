from django.contrib import admin
from .models import (
    Address, Category, Coupon, Order, OrderItem, Payment, Product, SizeVariations, Size, ShippingMethod
)


class SizeVariationsAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'stock']
    list_filter = ['product', 'size']
    search_fields = ['product__title']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent', 'code',
                    'valid_from', 'valid_to', 'active', ]
    list_filter = ['active', 'valid_from', 'valid_to', 'percent']
    search_fields = ['code']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'price', 'active', 'created', 'updated']
    list_filter = ['active', 'created', 'updated', 'price']
    search_fields = ['title']


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'address_line_1',
        'address_line_2',
        'city',
        'zip_code',
        'address_type',
    ]


admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Product)
admin.site.register(Size)
admin.site.register(SizeVariations, SizeVariationsAdmin)
admin.site.register(ShippingMethod)
