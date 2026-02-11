from django.contrib import admin
from .models import Product, Category, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Admin list lo kanipinche columns
    list_display = ('name', 'price', 'category')
    
    # Filter cheyadaniki side bar
    list_filter = ('category',)
    
    # Search box functionality
    # ForeignKey ayithe '__name' ani vaadaali
    search_fields = ('name', 'category__name') 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at')
    list_filter = ('created_at',)