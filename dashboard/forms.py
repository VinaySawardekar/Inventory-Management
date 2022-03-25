from attr import fields
from django import forms
from .models import Notification, Product, Order, Supplier

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'price']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name','email','phone_no','product', 'order_quantity']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name','category', 'mobile_no', 'email']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'notification']