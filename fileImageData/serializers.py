from rest_framework import serializers
from .models import CollectedProduct, Users, ParentInvoice
from .models import Customers, ProductList

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source = 'category_name.category_name')
    class Meta:
        model = ProductList
        fields = ['code', 'id', 'item_name', 'category_name', 'dimention', 'warehouse', 'qty_in_wh', 'price', 'image_urel']
class CollectedProductSerializer(serializers.ModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(queryset=ParentInvoice.objects.all())
    product_ID = serializers.PrimaryKeyRelatedField(queryset=ProductList.objects.all())
    class Meta:
        model = CollectedProduct
        fields= ['invoice','product_ID','quantity','price']

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id','identification','customer_name','customer_address','discount']