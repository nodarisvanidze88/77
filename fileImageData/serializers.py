from rest_framework import serializers
from .models import CollectedProduct
from .models import Customers

class CollectedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectedProduct
        fields= ['user','customer_info','product_ID','quantity', 'date']

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id','identification','customer_name','customer_address']