from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.index, name='dashboard-index'),
    path('add-to-cart/',views.addtocart, name='dashboard-add-to-cart'),
    path('staff/', views.staff, name ='dashboard-staff'),
    path('staff/detail/<int:pk>/', views.staff_detail, name ='dashboard-staff-detail'),
    path('staff/order-details/<int:pk>/', views.staff_order_details, name='dashboard-order-detail-by-staff'),
    path('product/', views.product, name ='dashboard-product'),
    path('product/delete/<int:pk>/', views.product_delete, name ='dashboard-product-delete'),
    path('product/update/<int:pk>/', views.product_update, name ='dashboard-product-update'),
    path('order/', views.order, name ='dashboard-order'),
    path('order/delete/<int:pk>', views.order_delete, name ='dashboard-order-delete'),
    path('reports/', views.reports , name='dashboard-reports'),
    path('my-notifications/', views.mynotifications, name='dashboard-my-notification'),
    path('my-notifications/mark-as-read/<int:pk>/', views.markasread, name='dashboard-my-notification-mark-as-read'),
    path('trends/', views.trends , name='dashboard-trends'),
    path('invoices/', views.getinvoices, name='dashboard-invoices'),
    path('invoice/delete/<int:pk>/', views.invoice_delete, name ='dashboard-invoice-delete'),
    path('invoice/view/', views.invoice_view, name ='dashboard-invoice-view'),
    path('myinvoices', views.myinvoices, name='dashboard-staff-myinvoice'),

    # path('supplier/',views.supplier, name='dashboard-supplier')
]