
from django.contrib import admin
from .models import Product, Order, Category, Supplier, Notification, Invoices
from django.contrib.auth.models import Group

admin.site.site_header = 'Inventory Dashboard'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category','quantity')
    list_filter = ['category',]

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Notification)
admin.site.register(Invoices)
#admin.site.unregister(Group)
