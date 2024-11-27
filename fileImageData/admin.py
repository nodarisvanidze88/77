from django.contrib import admin
from .models import ProductList, Users, CollectedProduct, Customers
# Register your models here.
admin.site.register({ProductList,Users, CollectedProduct, Customers})
