from django.contrib import admin
from django.utils.html import format_html
from .models import ProductList, Users, CollectedProduct, Customers, Product_Category, MissingPhoto, ParentInvoice
from .download_xlsx import get_excel_file, get_invoice_excel
from django.db.models import Sum
from django.urls import reverse, path
from django.utils.html import format_html
from .views import download_images_by_category_view_new
from django.utils.safestring import mark_safe
class Product_Admin_View(admin.ModelAdmin):
    list_display = ['code', 'id', 'item_name', 'category_name', 
                    'dimention', 'warehouse', 'qty_in_wh', 'price', 'display_image']
    search_fields =['code', 'id', 'item_name', 'category_name__category_name', 
                    'dimention', 'warehouse', 'qty_in_wh', 'price']
    list_filter = ['category_name__category_name']
    def display_image(self, obj):
        if obj.image_urel:
            return format_html('<img src="{}" style="width:100px; height=auto;"/>', obj.image_urel)
        return 'No Image'
    
    display_image.short_description='Image'

    def save_model(self, request, obj, form, change):
        # Generate the image URL based on the product ID
        obj.image_urel = f"https://storage.googleapis.com/nodari/{obj.id}.jpg"
        super().save_model(request, obj, form, change)

class Missing_Photo_Admin_View(admin.ModelAdmin):
    list_display = [
        'product_code', 
        'product_id', 
        'product_item_name', 
        'product_category_name', 
        'product_dimention', 
        'product_warehouse', 
        'product_qty_in_wh', 
        'product_price'
    ]
    search_fields = [
        'product__code', 
        'product__id', 
        'product__item_name', 
        'product__category_name__category_name', 
        'product__dimention', 
        'product__warehouse', 
        'product__qty_in_wh', 
        'product__price'
    ]
    list_filter = ['product__category_name__category_name']
    @admin.display(ordering='product__code', description='Code')
    def product_code(self, obj):
        return obj.product.code

    @admin.display(ordering='product__id', description='ID')
    def product_id(self, obj):
        return obj.product.id

    @admin.display(ordering='product__item_name', description='Item Name')
    def product_item_name(self, obj):
        return obj.product.item_name

    @admin.display(ordering='product__category_name__category_name', description='Category')
    def product_category_name(self, obj):
        return obj.product.category_name.category_name

    @admin.display(ordering='product__dimention', description='Dimension')
    def product_dimention(self, obj):
        return obj.product.dimention

    @admin.display(ordering='product__warehouse', description='Warehouse')
    def product_warehouse(self, obj):
        return obj.product.warehouse

    @admin.display(ordering='product__qty_in_wh', description='Quantity')
    def product_qty_in_wh(self, obj):
        return obj.product.qty_in_wh

    @admin.display(ordering='product__price', description='Price')
    def product_price(self, obj):
        return obj.product.price
    
    actions=['export_missing_photo_to_excel']

    @admin.action(description='Export Missing Photos to Excel')
    def export_missing_photo_to_excel(self,request,queryset):
        all_missing_photos = MissingPhoto.objects.all()
        return get_excel_file(query=all_missing_photos)

class CollectedItemsAdmin(admin.ModelAdmin):
    list_display = ['invoice','product_ID_id','quantity','price','total','status']
    search_fields =['invoice__invoice','product_ID__id','status']
    list_filter = ['status']

class CollectedProductInline(admin.TabularInline):
    model = CollectedProduct
    extra = 1

class ParentInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'date','customer_info','sum_total','status')
    search_fields = ['invoice','customer_info__customer_name','status']
    list_filter = ['status']
    inlines = [CollectedProductInline]
    def sum_total(self, obj):
        return CollectedProduct.objects.filter(invoice=obj).aggregate(Sum('total'))['total__sum'] or 0
    
    sum_total.short_description = 'Sum of Products' 

    actions=['export_invoice_excel']

    @admin.action(description='Export Invoice to Excel')
    def export_invoice_excel(self,request,queryset):
        custom_query = queryset.values().values_list('invoice','customer_info','status','date')
        return get_invoice_excel(query=custom_query)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['user','status','vizer']
    search_fields =['user']
    list_filter = ['status','vizer']

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'get_total_products','download_images_link']

    def get_total_products(self, obj):
        return obj.get_total

    get_total_products.short_description = 'Total Products'

    def download_images_link(self, obj):
        if obj.rar_file_url:
            return mark_safe(f'<a href="{obj.rar_file_url}" target="_blank" class="button">Download RAR File</a>')
        else:
            return mark_safe(f'''
                <form action="{reverse('download-images-by-category')}" method="get" onsubmit="disableButton(this)">
                    <input type="hidden" name="id" value="{obj.id}">
                    <button type="submit" style="background: #28a745; color: white; padding: 5px 10px; border: none; cursor: pointer;">
                        Generate & Download RAR ({obj.get_total})
                    </button>
                </form>
                <script>
                    function disableButton(form) {{
                        let button = form.querySelector("button");
                        button.disabled = true;
                        button.innerText = "Processing...";
                    }}
                </script>
            ''')


    download_images_link.short_description = "Download Images"
    # download_images_link.allow_tags = True

admin.site.register(ProductList, Product_Admin_View)
admin.site.register(Users, UsersAdmin)
admin.site.register(CollectedProduct, CollectedItemsAdmin)
admin.site.register(Customers)
admin.site.register(MissingPhoto,Missing_Photo_Admin_View)
admin.site.register(ParentInvoice, ParentInvoiceAdmin)
admin.site.register(Product_Category, ProductCategoryAdmin)