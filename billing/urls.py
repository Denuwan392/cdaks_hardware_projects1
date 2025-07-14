from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transaction/', views.record_transaction, name='record_transaction'),
    path('receipt/<int:transaction_id>/', views.receipt, name='receipt'),
    path('cashier/', views.cashier, name='cashier'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get_fruit/', views.get_detected_fruit, name='get_detected_fruit'),
    path('api/price/', views.get_item_price, name='get_item_price'),
    path('api/price', views.get_price, name='get_price'),

      
    
]