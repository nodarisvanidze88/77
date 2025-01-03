from rest_framework import serializers
from .models import CollectedProduct, Users, ParentInvoice
from .models import Customers, ProductList
from django.utils.timezone import localtime

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source = 'category_name.category_name')
    class Meta:
        model = ProductList
        fields = ['code', 'id', 'item_name', 'category_name', 'dimention', 'warehouse', 'qty_in_wh', 'price', 'image_urel']
class CollectedProductSerializer(serializers.ModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(queryset=ParentInvoice.objects.all())
    product_ID = serializers.PrimaryKeyRelatedField(queryset=ProductList.objects.all())
    qty_in_wh = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    class Meta:
        model = CollectedProduct
        fields = ['id','invoice', 'product_ID', 'quantity', 'price', 'qty_in_wh','total','status','image_url']

    def get_image_url(self, obj):
        return obj.product_ID.image_urel if obj.product_ID.image_urel else None
    def get_qty_in_wh(self, obj):
        return obj.product_ID.qty_in_wh if obj.product_ID.qty_in_wh else None
    def get_total(self, obj):
        return obj.quantity * obj.price
class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id','identification','customer_name','customer_address','discount']

class PharentInvoiceSerializer(serializers.ModelSerializer):
    customer_info = serializers.PrimaryKeyRelatedField(queryset=Customers.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    class Meta:
        model = ParentInvoice
        fields = ['invoice','customer_info','user','date','status', 'get_total']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.date:
            local_date_time =localtime(instance.date)
            representation['date'] = local_date_time.strftime('%Y-%m-%d %I:%M %p')
        return representation