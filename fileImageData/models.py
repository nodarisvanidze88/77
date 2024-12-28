from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
class Product_Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.category_name
    
# Create your models here.
class ProductList(models.Model):
    code = models.CharField(max_length=50)
    id = models.CharField(primary_key=True, max_length=50, unique=True)
    item_name = models.CharField(max_length=200)
    category_name = models.ForeignKey(Product_Category, on_delete=models.CASCADE, related_name='category')
    dimention = models.CharField(max_length=50)
    warehouse = models.CharField(max_length=50)
    qty_in_wh = models.FloatField() 
    price = models.FloatField()
    image_urel = models.URLField(null=True, blank=True)
    def __str__(self):
        return f"{self.id} - {self.item_name} - Qty: {self.qty_in_wh}"

class MissingPhoto(models.Model):
    product = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    def __str__(self):
        return self.product.item_name
    
class Users(models.Model):
  USER_STATUS= [('Valid','Valid'),
                ('Invalid','Invalid')]
  user = models.CharField(max_length = 50, unique=True)
  status = models.CharField(max_length=50, choices=USER_STATUS, default='Valid')
  vizer = models.BooleanField(default=False)
  def __str__(self):
        return self.user
  
class Customers(models.Model):
    identification = models.CharField(max_length=11, unique=True)
    customer_name = models.CharField(max_length=50)
    customer_address = models.CharField(max_length=200)
    discount = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'({self.identification}) - {self.customer_name}'
    

class ParentInvoice(models.Model):
    ORDER_STATUSES= [('Open','Open'),
                     ('Confirmed','Confirmed'),
                     ('Delivered','Delivered'),
                     ('Canceled','Canceled')]
    invoice = models.CharField(max_length=50, unique=True)
    customer_info = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='customer_Info')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='supervizer')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUSES, default='Open')

    def __str__(self):
        return self.invoice
    @property
    def get_total(self):
        return self.collectedproduct_set.aggregate(Sum('total'))['total__sum']
    
class CollectedProduct(models.Model):
    ORDER_STATUSES= [('Available','Available'),
                     ('Missing','Missing'),]
    invoice = models.ForeignKey(ParentInvoice, on_delete=models.CASCADE)
    product_ID = models.ForeignKey(ProductList, on_delete=models.CASCADE, related_name='selectedItem')
    quantity = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField()
    status = models.CharField(max_length=50, choices=ORDER_STATUSES, default='Available') 


    def __str__(self):
        return f"{self.invoice} {self.product_ID} {self.quantity}"

    def save(self, *args, **kwargs):
        total = (Decimal(self.price) * Decimal(self.quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        discount = (Decimal(total)*Decimal(self.invoice.customer_info.discount/100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.total = total - discount
        super().save(*args, **kwargs)

