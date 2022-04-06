from django.db import models
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your models here.
CATEGORY = (
    ('Fashion accessories', 'Fashion accessories'),
    ('Health and beauty', 'Health and beauty'),
    ('Food and beverages', 'Food and beverages'),
    ('Home and lifestyle','Home and lifestyle'),
    ('Sports and travel','Sports and travel')
    

) 


class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY, null=True)
    quantity = models.PositiveIntegerField(null=True)
    price = models.PositiveBigIntegerField(null=True)


    class Meta:
        verbose_name_plural = 'Product'
    
    def __str__(self):
        return f'{self.name}-{self.quantity}-₹{self.price}-per pc'
 



class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone_no = models.BigIntegerField(null=True)
    staff = models.ForeignKey(User, models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    total_price = models.PositiveBigIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Order'


    def __str__(self):
        return f'{self.product} ordered by {self.staff.username} of Rs.{self.total_price}'


class Supplier(models.Model):
    category = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100, null=True)
    mobile_no = models.BigIntegerField(null=True)
    email = models.EmailField(null=True)

    class Meta:
        verbose_name_plural = 'Supplier'


    def __str__(self):
        return f'{self.category}'


class Category(models.Model):
    name = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = 'Category'

    def __str__(self):
        return f'{self.name}'

class Notification(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True)
    notification = models.CharField(max_length=1000, null=True)
    is_seen = models.BooleanField(default=False)
    visible_to = models.CharField(max_length=20,null=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        noti_obj = Notification.objects.filter(is_seen = False).count()
        data = {'count': noti_obj ,'current': self.notification}
        print(data)
        # async_to_sync(channel_layer.group_send(

        # ))
        super(Notification, self).save(*args, **kwargs)

class Invoices(models.Model):
    invoice_id = models.CharField(max_length=100, null=True, unique=True)
    product = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone_no = models.BigIntegerField(null=True)
    staff = models.CharField(max_length=100, null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    price = models.PositiveBigIntegerField(null=True)
    total_price = models.PositiveBigIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    temp_id = models.IntegerField(null=True)
    temp_id_2 = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f'{self.invoice_id}'