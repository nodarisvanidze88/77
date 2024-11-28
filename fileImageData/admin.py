from django.contrib import admin
from django.utils.html import format_html
from .models import ProductList, Users, CollectedProduct, Customers, Product_Category
# Register your models here.
class Product_Admin_View(admin.ModelAdmin):
    list_display = ['code', 'id', 'item_name', 'category_name', 
                    'dimention', 'warehouse', 'qty_in_wh', 'price', 'display_image']
    search_fields =['code', 'id', 'item_name', 'category_name__category_name', 
                    'dimention', 'warehouse', 'qty_in_wh', 'price']
    
    def display_image(self, obj):
        if obj.image_urel:
            return format_html('<img src="{}" style="width:100px; height=auto;"/>', obj.image_urel)
        return 'No Image'
    
    display_image.short_description='Image'

admin.site.register(ProductList, Product_Admin_View)
admin.site.register(Users)
admin.site.register(CollectedProduct)
admin.site.register(Customers)
admin.site.register(Product_Category)
