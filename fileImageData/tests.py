from django.test import TestCase

# Create your tests here.
from .models import ProductList

items = ProductList.objects.all()