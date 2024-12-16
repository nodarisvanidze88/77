from django.db import models

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
        return self.item_name

class MissingPhoto(models.Model):
    product = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    def __str__(self):
        return self.product.item_name
    
class Users(models.Model):
  user = models.CharField(max_length = 50, unique=True)

  def __str__(self):
        return self.user


  
class Customers(models.Model):
    identification = models.CharField(max_length=11, unique=True)
    customer_name = models.CharField(max_length=50)
    customer_address = models.CharField(max_length=200)

    def __str__(self):
        return f'({self.identification}) - {self.customer_name}'
    

class ParentInvoice(models.Model):
    ORDER_STATUSES= [('Open','Open'),
                     ('Confirmed','Confirmed'),
                     ('Delivered','Delivered'),
                     ('Canceled','Canceled')]
    invoice = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUSES, default='Open')

    def __str__(self):
        return self.invoice
    
class CollectedProduct(models.Model):
    ORDER_STATUSES= [('Available','Available'),
                     ('Missing','Missing'),]
    invoice = models.ForeignKey(ParentInvoice, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='supervizer')
    customer_info = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='customer_Info')
    product_ID = models.ForeignKey(ProductList, on_delete=models.CASCADE, related_name='selectedItem')
    quantity = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField()
    status = models.CharField(max_length=50, choices=ORDER_STATUSES, default='Available') 


    def __str__(self):
        return f"{self.invoice} {self.user} {self.customer_info} {self.product_ID} {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

