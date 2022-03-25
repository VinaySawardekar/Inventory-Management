from itertools import count
from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Supplier, Notification, Invoices
from .forms import ProductForm, OrderForm, SupplierForm, NotificationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .filters import ProductFilter
from .utils import email_notify,generateinvoice

# Create your views here.

@login_required
def index(request):
    orders = Order.objects.all()
    products = Product.objects.all()
    orders_count = orders.count()
    product_count = Product.objects.all().count()
    workers_count = User.objects.all().count()
    latest_order = Order.objects.all().order_by('-date')[:4]
    predict_category = predict()

    if request.method=='POST':
        form = OrderForm(request.POST)
        product_id = request.POST['product']
        order_quantity =  request.POST['order_quantity']
        buyer_name = request.POST['name']
        buyer_email = request.POST['email']
        buyer_phone = request.POST['phone_no']
        product = Product.objects.filter(pk = product_id)
        str1 = product[0]
        str2 = str(str1).split('-')
        price = str2[2]
        price = price.replace('₹', '')
        total_price= int(price) * int(order_quantity) 
        total_inc_gst = int(total_price + (18*total_price/100))
        pdp_count = str2[1]

        if int(pdp_count) == 0:
            context={
                'message':'Out of Stock. Please Order Another Product',
                'orders':orders,
                'form':form,
                'products': products,
                'products_count':product_count,
                'workers_count':workers_count,
                'orders_count':orders_count,
                'latest_order':latest_order,
                'predict_category':predict_category
            }
        elif int(order_quantity)<=int(pdp_count):
            if form.is_valid():
                remain_count = int(pdp_count)-int(order_quantity)
                if int(remain_count) < 30:
                    subject = f'Please Restock Your Product: {str2[0]} ' 
                    body = f'Hi Admin , Your Stock quantity of the product {str2[0]} is  "{int(pdp_count) - int(order_quantity)}". Please Re-stock it as soon as possible.'
                    to = 'pooja.mane101099@gmail.com'
                    email_notify(subject,body,to)
                    notif = Notification(user=request.user, notification=f'Your Stock quantity of the product {str2[0]} is  "{int(pdp_count) - int(order_quantity)}". Please Re-stock it as soon as possible.', visible_to ='Admin')
                    notif.save()
                instance = form.save(commit=False)
                instance.staff = request.user
                instance.total_price = int(total_inc_gst)
                update_product = Product.objects.get(pk = product_id)
                update_product.quantity = remain_count
                update_product.save()
                instance.save()
                # subject = 'Order Confirmed' 
                # new_line = '\n'
                # body = f'Hi {buyer_name} , Your Order is Successfully Placed for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_price} {new_line} {new_line} Thanks & Regards, {new_line} Inventory System'
                # to = buyer_email
                # email_notify(subject,body,to)
                # messages.success(request, f'Your Request is Placed for Product {str2[0]}')
                get_invoice, invoice_no , invoice_id = generateinvoice(str2[0], order_quantity,total_price, total_inc_gst, buyer_name, buyer_email, buyer_phone, request.user)
                subject = 'Order Confirmed' 
                new_line = '\n'
                # body = f'Hi {buyer_name} , Your Order is Successfully Placed  for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_price} {new_line} {new_line} Thanks & Regards, {new_line} Inventory System'
                body = f'Hi {buyer_name} , Your Order is Successfully Placed. {new_line} Here is Your Detailed Invoice:{new_line}{get_invoice}'
                to = buyer_email
                email_notify(subject,body,to)
                messages.success(request, f'Your Request is Placed for Product {str2[0]} , Invoice Id: {invoice_no}')
                notif = Notification(user=request.user, notification=f'Order is Successfully Placed for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_inc_gst}', visible_to =request.user)
                notif.save()
                return redirect('dashboard-invoice-view',pk = invoice_id)
        elif int(order_quantity) > int(pdp_count):
            notif_data_all = Notification.objects.filter(visible_to=request.user)
            notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
            notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
            context={
                'message':'Quantity Limit Exceed. You Can Order Max to Half of the Available quantity',
                'orders':orders,
                'form':form,
                'products': products,
                'products_count':product_count,
                'workers_count':workers_count,
                'orders_count':orders_count,
                'latest_order':latest_order,
                'notif_data': notif_data,
                'notif_count': notif_count,
                'notif_data_all': notif_data_all,
                'predict_category':predict_category
            }
        else:
            notif_data_all = Notification.objects.filter(visible_to=request.user)
            notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
            notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
            context={
                'message1':f'Quantity Limit Exceed. You can order {pdp_count} quantity of {str2[0]} .',
                'orders':orders,
                'form':form,
                'products': products,
                'products_count':product_count,
                'workers_count':workers_count,
                'orders_count':orders_count,
                'latest_order':latest_order,
                'notif_data': notif_data,
                'notif_count': notif_count,
                'notif_data_all': notif_data_all,
                'predict_category':predict_category
            }
        return render(request, 'dashboard/index.html', context)
    else:
        form = OrderForm()

    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    context={
        'orders':orders,
        'form':form,
        'products': products,
        'products_count':product_count,
        'workers_count':workers_count,
        'orders_count':orders_count,
        'latest_order':latest_order,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
        'predict_category':predict_category
  }
    return render(request, 'dashboard/index.html', context)



@login_required
def staff(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    workers = User.objects.all()
    workers_count = workers.count()
    orders_count = Order.objects.all().count()
    product_count = Product.objects.all().count()
    staff_count = Product.objects.all().count()
    context={
        'workers': workers,
        'workers_count': workers_count,
        'orders_count': orders_count,
        'product_count': product_count,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/staff.html', context)

def staff_detail(request, pk):
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    workers = User.objects.get(id=pk)
    context={
        'workers':workers,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/staff_detail.html', context)

@login_required
def product(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    items = Product.objects.all() #Using ORM  
    product_count = items.count()
    #items = Product.objects.raw('SELECT * FROM dashboard_product')

    workers_count = User.objects.all().count()
    orders_count = Order.objects.all().count

    if request.method =='POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            product_name = form.cleaned_data.get('name')
            messages.success(request, f'{product_name} has been added')
            return redirect('dashboard-product')
    else:
        form = ProductForm()

    myFilter = ProductFilter(request.GET, queryset=items)
    items = myFilter.qs
    context = {
        'items': items,
        'form': form,
        'workers_count': workers_count,
        'product_count': product_count,
        'myFilter':myFilter,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/product.html', context)

@login_required
def product_delete(request, pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    item = Product.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        messages.error(request , 'Product has been deleted Successfully!')
        return redirect('dashboard-product')
    context = {
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/product_delete.html', context)

@login_required
def product_update(request, pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    item = Product.objects.get(id=pk)
    if request.method=='POST':
        form = ProductForm(request.POST, instance=item)
        order_quantity =  request.POST['quantity']
        product = Product.objects.filter(pk = pk)
        str1 = product[0]
        str2 = str(str1).split('-')
        pdp_count = str2[1]
        if form.is_valid():
            added_count = int(pdp_count)+int(order_quantity)
            update_product = Product.objects.get(pk = pk)
            update_product.quantity = added_count
            update_product.save()
            messages.success(request, f'Product Quantity of {str2[0]} is Updated Successfully!')
            return redirect('dashboard-product')
    else:
        form = ProductForm(instance=item)
    context={
        'form':form,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/product_update.html', context)

@login_required
def order(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    orders = Order.objects.all().order_by('date')
    orders_count = orders.count
    workers_count = User.objects.all().count()
    product_count = Product.objects.all().count()
    context={
        'orders':orders,
        'workers_count':workers_count,
        'orders_count':orders_count,
        'product_count':product_count,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,

    }
    return render(request, 'dashboard/order.html', context)

def reports(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    orders = Order.objects.all()
    products = Product.objects.all()
    orders_count = orders.count()
    product_count = Product.objects.all()
    workers_count = User.objects.all().count()

    context={
        'orders':orders,
        'products': products,
        'products_count':product_count,
        'workers_count':workers_count,
        'orders_count':orders_count,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
        }
    return render(request, 'dashboard/reports.html', context)


def staff_order_details(request,pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    orders = Order.objects.all()
    user = User.objects.get(id = pk)
    print(user)
    products = Product.objects.all()
    context={
        'user_name':user,
        'orders':orders,
        'products': products,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/order_details_user.html', context)

# def supplier(request):
#     supplier_details = Supplier.objects.all()
#     if request.method == 'POST':
#         form = SupplierForm(request.POST)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             # instance.staff = request.user
#             instance.save()
#             messages.success(request, f'Supplier is Added')
#             return redirect('dashboard-supplier')
#     else:
#         form = SupplierForm()
#     context = {
#         'form' :form,
#         'supplier_details': supplier_details}
#     return render(request, 'dashboard/supplier.html', context)

# def set_categories():
#     # supplier_details = Supplier.objects.all()
#     # print(list(supplier_details))
#     # a = []
#     # for b in supplier_details.values():
#     #     a.append(b['category'])
#     # print(a)
#     # return a
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             category = request.POST['category']

def mynotifications(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user).order_by('-date')
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    context={
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
  }
    return render(request, 'dashboard/my_notification.html', context)

def markasread(request,pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    context={
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    item = Notification.objects.get(id=pk)
    item.is_seen = True
    item.save()
    messages.success(request , 'Marked as Read Successfully!')
    return render(request, 'dashboard/my_notification.html', context)


def trends(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    context={
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/trends.html', context)

def predict():
    import pandas as pd
    import numpy as np
    from sklearn import linear_model
    from sklearn.preprocessing import LabelEncoder

    df = pd.read_csv('supermarket_sales.csv')

    le = LabelEncoder()
    category_encoded = le.fit_transform(df['Category'])
    df['category_encoded']= category_encoded
    reg = linear_model.LinearRegression()
    reg.fit(df[['Date','category_encoded']],df.Price)
    from datetime import datetime
    currentMonth = datetime.now().month
    price = []
    for i in range(0,6):
        predict = reg.predict([[currentMonth,i]])
        price.append(predict)

    max_value = max(price)
    max_index = price.index(max_value)
    if max_index == 1:
        cat = 'Fashion accessories'
    elif max_index == 2:
        cat = 'Food and beverages'
    elif max_index == 3:
        cat = 'Health and beauty'
    elif max_index == 4:
        cat = 'Home and lifestyle'
    elif max_index == 5:
        cat = 'Sports and travel'
    
    return cat
    

def getinvoices(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user).order_by('-date')
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    items = Invoices.objects.all()
    context={
        'items':items,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
  }
    return render(request, 'dashboard/invoices.html', context)

def invoice_delete(request, pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    item = Invoices.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        messages.error(request , 'Invoice has been deleted Successfully!')
        return redirect('dashboard-invoices')
    context = {
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/invoice_delete.html', context)

def invoice_view(request, pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    item = Invoices.objects.get(id=pk)
    # if request.method=='POST':
    #     item.delete()
    #     messages.error(request , 'Invoice has been deleted Successfully!')
    #     return redirect('dashboard-invoices')
    gst_amount = item.total_price - item.price
    price_per_item = item.price/item.order_quantity
    context = {
        'price_per_item':int(price_per_item),
        'gst_amount':gst_amount,
        'gst_no':'18AABCU9603R1ZM',
        'item': item,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/invoice_view.html', context)

def myinvoices(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user).order_by('-date')
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    items = Invoices.objects.all()
    context={
        'items':items,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
  }
    return render(request, 'dashboard/myinvoices.html', context)

def order_delete(request, pk):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    item = Order.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        messages.error(request , f'Order id "{pk}" has been deleted Successfully!')
        return redirect('dashboard-order')
    context = {
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'dashboard/order_delete.html', context)
    