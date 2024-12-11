from rest_framework import serializers
from .models import CollectedProduct
from .models import Customers, ProductList

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source = 'category_name.category_name')
    class Meta:
        model = ProductList
        fields = ['code', 'id', 'item_name', 'category_name', 'dimention', 'warehouse', 'qty_in_wh', 'price', 'image_urel']
class CollectedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectedProduct
        fields= ['invoice','user','customer_info','product_ID','quantity', 'date', 'status']

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id','identification','customer_name','customer_address']