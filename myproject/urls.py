from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login_view'), 
    path('logout/', views.logout_view, name='logout_view'), 
    
    
    path('cart/', views.view_cart, name='view_cart'), 
    
    path('payment/', views.payment_page, name='payment_page'),
    path('place-order/', views.place_order, name='place_order'),
    path('orders/', views.order_list, name='order_list'),
    path('remove-item/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-quantity/<int:product_id>/', views.add_quantity, name='add_quantity'),
    path('reduce-quantity/<int:product_id>/', views.reduce_quantity, name='reduce_quantity'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)