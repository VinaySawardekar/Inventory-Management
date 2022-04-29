from itertools import count
from typing import List
from unicodedata import name
from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Supplier, Notification, Invoices
from .forms import ProductForm, OrderForm, SupplierForm, NotificationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .filters import ProductFilter
from .utils import Predict,predicT, email_notify,generateinvoice, render_to_pdf

# Create your views here.

@login_required
def index(request):
    orders = Order.objects.all()
    products = Product.objects.all()
    orders_count = orders.count()
    product_count = Product.objects.all().count()
    workers_count = User.objects.all().count()
    latest_order = Order.objects.all().order_by('-date')[:4]
    predict_category,predict_product,festeev  = predict()

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
                'predict_category':predict_category,
                'predict_product':predict_product,
                 'festival':festeev
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
                # subject = 'Order Confirmed' 
                new_line = '\n'
                # # body = f'Hi {buyer_name} , Your Order is Successfully Placed  for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_price} {new_line} {new_line} Thanks & Regards, {new_line} Inventory System'
                # body = f'Hi {buyer_name} , Your Order is Successfully Placed. {new_line} Here is Your Detailed Invoice:{new_line}{get_invoice}'
                # to = buyer_email
                # email_notify(subject,body,to)
                messages.success(request, f'Your Request is Placed for Product {str2[0]} , Invoice Id: {invoice_no}')
                notif = Notification(user=request.user, notification=f'Order is Successfully Placed for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_inc_gst}', visible_to =request.user)
                notif.save()
                return redirect('dashboard-add-to-cart')
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
                'predict_category':predict_category,
                'predict_product':predict_product,
                'festival':festeev
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
                'predict_category':predict_category,
                'predict_product':predict_product,
                'festival':festeev
            }
        return render(request, 'dashboard/addtocart.html', context)
    else:
        latest_order = Order.objects.all().order_by('-date')[:1]
        # print(latest_order)
        for i in latest_order:
            print(i.name, i.email)
        # form = OrderForm(initial={'name':i.name, 'email':i.email, 'phone_no':i.phone_no})
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
        'predict_category':predict_category,
        'predict_product':predict_product,
        'festival':festeev
}
    return render(request, 'dashboard/index.html', context)

def addtocart(request):
    orders = Order.objects.all()
    products = Product.objects.all()
    orders_count = orders.count()
    product_count = Product.objects.all().count()
    workers_count = User.objects.all().count()
    latest_order = Order.objects.all().order_by('-date')[:4]
    predict_category,predict_product,festeev = predict()
    latest_order = Order.objects.all().order_by('-date')[:1]
    # print(latest_order)

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
                'predict_category':predict_category,
                'predict_product':predict_product
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
                # subject = 'Order Confirmed' 
                new_line = '\n'
                # # body = f'Hi {buyer_name} , Your Order is Successfully Placed  for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_price} {new_line} {new_line} Thanks & Regards, {new_line} Inventory System'
                # body = f'Hi {buyer_name} , Your Order is Successfully Placed. {new_line} Here is Your Detailed Invoice:{new_line}{get_invoice}'
                # to = buyer_email
                # email_notify(subject,body,to)
                messages.success(request, f'Your Request is Placed for Product {str2[0]} , Invoice Id: {invoice_no}')
                notif = Notification(user=request.user, notification=f'Order is Successfully Placed for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_inc_gst}', visible_to =request.user)
                notif.save()
                return redirect('dashboard-add-to-cart')
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
                'predict_category':predict_category,
                'predict_product':predict_product
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
                'predict_category':predict_category,
                'predict_product':predict_product
            }
        return render(request, 'dashboard/addtocart.html', context)
    else:
        # latest_order = Order.objects.all().order_by('-date')[:1]
        # # print(latest_order)
        # for i in latest_order:
        #     print(i.name, i.email)
        # form = OrderForm(initial={'name':i.name, 'email':i.email, 'phone_no':i.phone_no})
        # form = OrderForm()

#     notif_data_all = Notification.objects.filter(visible_to=request.user)
#     notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
#     notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
#     context={
#         'orders':orders,
#         'form':form,
#         'products': products,
#         'products_count':product_count,
#         'workers_count':workers_count,
#         'orders_count':orders_count,
#         'latest_order':latest_order,
#         'notif_data': notif_data,
#         'notif_count': notif_count,
#         'notif_data_all': notif_data_all,
#         'predict_category':predict_category
# }
#     return render(request, 'dashboard/index.html', context)

        for i in latest_order:
            print(i.name, i.email)
        form = OrderForm(initial={'name':i.name, 'email':i.email, 'phone_no':i.phone_no})
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
            'predict_category':predict_category,
            'predict_product':predict_product
    }
        return render(request, 'dashboard/addtocart.html', context)


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
    # print(df.head(10))
    from datetime import datetime
    import random
    currentMonth = datetime.now().month
    # currentMonth = 9
    price = []
    for i in range(0,6):
        predict = reg.predict([[currentMonth,i]])
        price.append(predict)
    # print(price)
    max_value = random.choice(price)
    max_index = price.index(max_value)
    print(max_index)
    cat = Predict(index=currentMonth)    

    df = pd.read_csv('festival.csv')

    le = LabelEncoder()
    product_encoded = le.fit_transform(df['Product'])
    # festival_encoded = le.fit_transform(df['Festival'])
    df['product_encoded']= product_encoded
    # df['festival_encoded'] = festival_encoded
    reg = linear_model.LinearRegression()
    reg.fit(df[['Date_Month','product_encoded']],df.Quantity)
    # print(df.head())
    from datetime import datetime
    currentMonth = datetime.now().month
    max_Index = datetime.now().month
    # max_Index = 8
    price = []
    for i in range(1,16):
        predict = reg.predict([[currentMonth,i]])
        price.append(predict)
    # print(price)
    max_value = max(price)
    max_index = price.index(max_value)
    prod_name = ''
    prod_name = predicT(max_Index)
    
    #Festival
    Electronic = ['AC', 'TV', 'Fridge', 'Mobiles','Decor']
    Ganesh = ['Sweets','Decor']
    Navratri = ['Clothes','Decor']
    Rakshabhandhan = ['Sweets', 'Clothes']
    Holi = ['Sweets', 'Clothes','Herbal Colors']
    festeev=''

    if prod_name in Ganesh and max_Index == 9:
        festeev = 'Ganesh Chathurthi'
    elif prod_name in Navratri and max_Index == 10:
        festeev = 'Navratri'
    elif prod_name in Rakshabhandhan and max_Index == 8:
        festeev = 'Rakshabhandhan'
    elif prod_name in Holi and max_Index == 3:
        festeev = 'Holi'
    elif prod_name in Electronic and max_Index == 11:
        festeev = 'Diwali'
    else:
        festeev = 'Offers & Discounts'
    

    return cat,prod_name,festeev
    

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

def invoice_view(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    item = Invoices.objects.values_list('temp_id', flat=True).order_by('-date')[:1]
    item_list = Invoices.objects.filter(temp_id=item)
    # print(item_list)

    # invoice_all = Invoices.objects.get().order_by('-date')[:1]
    temp_2 = Invoices.objects.values_list('temp_id_2', flat=True).order_by('-date')[:1]
    for i in temp_2:
        print(i)
    
    Invoices.objects.filter(temp_id_2 = i).update(temp_id_2 = i +1)
    # if request.method=='POST':
    #     item.delete()
    #     messages.error(request , 'Invoice has been deleted Successfully!')
    #     return redirect('dashboard-invoices')
    get_invoices = Invoices.objects.filter(temp_id = item)
    get_invoices_one = Invoices.objects.filter(temp_id = item)[:1]
    get_invoices_count = Invoices.objects.filter(temp_id = item).count()
    # print(get_invoices)
    list = {
        'invoice_id':'',
        'name':'',
        'email':'',
        'phone_no':'',
        'product':[],
        'date':'',
        'staff':'',
        'total_price_inc_gst':'',
        'total_price':'',
        'gst_amount':''
    }
    for i in get_invoices_one:
        list['invoice_id']= i.invoice_id
        list['name'] = i.name
        list['email'] = i.email
        list['phone_no'] = i.phone_no
        list['date'] = i.date
        list['staff'] = i.staff

    for j in get_invoices:
        # print(j)
        price_per_pc = j.price/j.order_quantity
        list['product'].append({'product_name':j.product , 'product_quant':j.order_quantity, 'price':j.price ,'total_price':j.total_price, 'price_per_pc':price_per_pc})

    sum = 0
    sum2 = 0
    for l in get_invoices:
        sum = sum + l.total_price
        sum2 = sum2 + l.price
    gst = sum - sum2
    list['total_price'] = sum2
    list['total_price_inc_gst'] = sum
    list['gst_amount'] = gst
    # print(list)
    
    # gst_amount = item.total_price - item.price
    # price_per_item = item.price/item.order_quantity
    context = {
        # 'price_per_item':int(price_per_item),
        # 'gst_amount':gst_amount,
        'gst_no':'18AABCU9603R1ZM',
        'item': list,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
     
    new_string=''
    new_line = '\n'
    for i in list['product']:
        # print(i)
        product_name = i['product_name']
        print(product_name)
        print(len(product_name))
        product_quant = i['product_quant']
        price = i['price']
        # "{:<15}".format(product_name)
        new_string = f"{product_name:<40} {product_quant:<22} ₹ {price} {new_line}" + f" {new_string}"
        
        # new_string % (product_name,product_quant, price)
    # new_string = MIMEText(new_string,'html')
    print(new_string)   
    # print(new_string)
    # html.format(product_name, product_quant, price)
    # part1 = MIMEText(text, 'plain')
    # part2 = MIMEText(html, 'html')
    
    
    # body = f"Hi {list['name']} , Your Order is Successfully Placed for Product:- {str2[0]} {new_line} Quantity :- {int(order_quantity)} {new_line} Total Amount(Inc. Gst) :- ₹ {total_price} {new_line} {new_line} Thanks & Regards, {new_line} Inventory System"
    body = f"Hi {list['name']} , Your Order is Successfully Placed. {new_line} Here is Your Detailed Invoice:{new_line} {new_line} INVENTORY MANAGEMENT SYSTEM {new_line} Shivajinagar,Pune {new_line} {new_line} Customer:- {list['name']} {new_line} {list['email']} {new_line} {list['phone_no']} {new_line} {new_line} GSTIN No. - 1234567890GHT {new_line} Invoice No.- {list['invoice_id']}{new_line}{new_line} {'Item':<40} {'Quantity':<22} Price {new_line} {new_string} {new_line} {'SubTotal':<63} ₹ {list['total_price']} {new_line} {'Gst':<65}  18% {new_line} {'Total':<67} ₹ {list['total_price_inc_gst']}  {new_line} {new_line} Staff Name:-{list['staff']} {new_line} Purchased On:- {list['date']} {new_line}{new_line} Thanks. Welcome Again \U0001F601"            
    # print(body)
    sendTo = f"{list['email']}"
    # sendTo = "vinaysawardekar99@gmail.com"
    # Create the root message and fill in the from, to, and subject headers
    sub= 'Purchase details'
    
    # pdf = render_to_pdf('dashboard/pdf.html',context)
    # print(pdf)
    email_notify(sub,body=body ,to=sendTo)
    #rendering the template
    # return HttpResponse(pdf, content_type='application/pdf')
    # return render(request, 'dashboard/pdf.html', context)
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
    