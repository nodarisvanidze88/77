from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import ProductList, Users
from django.db.models import Count
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.db.models import Case, When, Value, IntegerField
from .serializers import CollectedProductSerializer, CustomersSerializer, ProductListSerializer, PharentInvoiceSerializer
from .models import Customers, Product_Category, MissingPhoto, ParentInvoice, CollectedProduct
from .new_data import get_CSV_File_content
from .storage_content import list_files_in_bucket

@api_view(['GET'])
def getCSVFile(request):
  file = get_CSV_File_content()
  header_items = list(file.fieldnames)
  file_ids = set()
  for row in file:
    file_ids.add(row[header_items[1]])
    price = row[header_items[7]] if row[header_items[7]] else 0
    qty = row[header_items[6]] if float(price) > 0 else 0
    warehouse = row[header_items[5]] if row[header_items[5]] else "1"
    category, created = Product_Category.objects.get_or_create(category_name=row[header_items[3]])
    ProductList.objects.update_or_create(
                id=row[header_items[1]],
                defaults={
                    'code': row[header_items[0]],
                    'item_name': row[header_items[2]],
                    'category_name': category,
                    'dimention': row[header_items[4]],
                    'warehouse': warehouse,
                    'qty_in_wh': qty,
                    'price': price,
                    'image_urel': f"https://storage.googleapis.com/nodari/{row[header_items[1]]}.jpg"
                }
              )
  ProductList.objects.exclude(id__in=file_ids).update(qty_in_wh=0.0)
  resValue = JsonResponse({"message": 'Upload complete.'})
  return resValue

class ProductListView(APIView):
    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('category_id', None)
        missing_photos = MissingPhoto.objects.values_list('product_id', flat=True)
        queryset = ProductList.objects.filter(qty_in_wh__gt=0).exclude(id__in=missing_photos)
        if category_id and category_id != '-1':
          queryset = queryset.filter(category_name__id=category_id)
        else:
          queryset = queryset.order_by('category_name','id')
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class GetProductIDs(APIView):
   def get(self, request, *args, **kwargs):
      missing_photos = MissingPhoto.objects.values_list('product_id', flat=True)
      result = ProductList.objects.filter(qty_in_wh__gt=0).exclude(id__in=missing_photos).order_by('id').values_list('id',flat=True)
      return Response(result)

class GetOneProductDetails(APIView):
   def get(self, request, *args, **kwargs):
      query = request.query_params.get('id',None)
      try:
        result = ProductList.objects.get(id=query)
      except ProductList.DoesNotExist as e:
        return Response({"Message":e}, status=400)
      else:
        serializer = ProductListSerializer(result)
        return Response(serializer.data)
      
class CategoryCountsAPIView(APIView):
   def get(self, request, *args, **kwargs):
        category_counts = ProductList.objects.filter(qty_in_wh__gt=0).values(
           'category_name__id','category_name__category_name').annotate(
            product_count=Count('id')
        ).order_by('category_name__category_name')
        data = [{'id':-1,
                'category_name':'All',
                'product_count': sum(cat['product_count'] for cat in category_counts)}]
        for category in category_counts:
          data.append({'id':category['category_name__id'],
                       'category_name': category['category_name__category_name'],
                        'product_count': category['product_count'],
          })
        return Response(data)

@api_view(['GET'])
def getWithoutImage(request):
    if request.method=='GET':
        items = ProductList.objects.filter(image_urel="")
        data = [{
            'code': i.code,
            'product_id': i.id,
            'item_name': i.item_name,
            'category_name': i.category_name,
            'dimention': i.dimention,
            'warehouse': i.warehouse,
            'qty_in_wh': i.qty_in_wh,
            'price': i.price,
            'image_urel':i.image_urel,
                } for i in items]
        return JsonResponse(data, safe=False)
      
@api_view(['GET'])
def getUsers(request):
  if request.method=="GET":
    userList = Users.objects.all()
    data = list(userList.values())
    return JsonResponse(data, safe=False)
class GetUsers(APIView):
   def get(self, request, *args, **kwargs):
      ...

   
class CustomersList(viewsets.ModelViewSet):
  queryset = Customers.objects.all()
  serializer_class = CustomersSerializer
      
@api_view(['GET'])
def get_without_image_list(request):
  bucket_name = 'nodari'
  try:
    image_ids = list_files_in_bucket(bucket_name)
  except Exception as e:
    return Response({'error':str(e)}, status=500)
  else:
    product_without_images = ProductList.objects.exclude(id__in=image_ids)
    MissingPhoto.objects.all().delete()
    MissingPhoto.objects.bulk_create([
       MissingPhoto(product = product) for product in product_without_images
    ])
    return Response({"message": 'Generated list without photo'}, status=200)
  

class Get_pharent_invoice(APIView):
  def get(self, request, *args, **kwargs):
    customer_info = request.query_params.get('customer_info', None)
    mode = request.query_params.get('mode', None)
    if customer_info is None:
      return Response({"error": "Customer info is required"}, status=400)
    if mode == 'All' or mode is None or mode=='':
      invoice = ParentInvoice.objects.filter(customer_info=customer_info).annotate(
      status_order=Case(
          When(status='Open', then=Value(1)),
          When(status='Confirmed', then=Value(2)),
          When(status='Delivered', then=Value(3)),
          When(status='Canceled', then=Value(4)),
          output_field=IntegerField(),
      )).order_by('status_order','-date')
    else:
      invoice = ParentInvoice.objects.filter(customer_info=customer_info, status=mode).order_by('-date')
    serializer = PharentInvoiceSerializer(invoice, many=True)
    return Response(serializer.data)
  
  def put(self, request, *args, **kwargs):
    invoice = request.query_params.get('invoice', None)
    status = request.query_params.get('status', None)
    if invoice is None or status is None or status == 'Open' or status == '':
      return Response({"error": "Invoice is required"}, status=400)
    try:
      invoice_instance = ParentInvoice.objects.get(invoice=invoice)
      invoice_instance.status = status
      invoice_instance.save()
    except:
      return Response({"error": "Invoice not found"}, status=400)
    if status =='Confirmed':
      collected_products = CollectedProduct.objects.filter(invoice__invoice=invoice)
      for product in collected_products:
        product_item = ProductList.objects.get(id=product.product_ID.id)
        if product_item.qty_in_wh ==0 or product_item.qty_in_wh<product.quantity:
          product.status = 'Missing'
          product.save()
          continue
        product_item.qty_in_wh -= product.quantity
        product_item.save()
      return Response({"message": "Invoice status updated and changed quantities"}, status=200)
    return Response({"message": "Invoice status updated"}, status=200)
   
   
class Collected_products_viewset(APIView):
  def get(self, request, *args, **kwargs):
    invoice = request.query_params.get('invoice', None)
    if invoice is None:
      return Response({"error": "Invoice is required"}, status=400)
    collected_products = CollectedProduct.objects.filter(invoice__invoice=invoice)
    serializer = CollectedProductSerializer(collected_products, many=True)
    return Response(serializer.data)
  
  def put(self, request, *args, **kwargs):
    try:
        product_id = request.data.get('id')  # ID of the product to update
        new_quantity = request.data.get('quantity')  # New quantity value
        if not product_id or new_quantity is None:
            return Response({"error": "Product ID and Quantity are required"}, status=400)

        # Fetch the product instance
        collected_product = CollectedProduct.objects.get(id=product_id)
    except CollectedProduct.DoesNotExist:
        return Response({"error": "Collected product not found"}, status=404)

    try:
        # Update quantity
        collected_product.quantity = int(new_quantity)
        # Save the instance, which automatically recalculates the total
        collected_product.save()
    except (ValueError, TypeError):
        return Response({"error": "Invalid data for quantity"}, status=400)

    # Serialize and return the updated data
    serializer = CollectedProductSerializer(collected_product)
    return Response(serializer.data, status=200)

  def post(self, request, *args, **kwargs):
    collected_data = request.data['collected_data']
    try:
        invoice_number = collected_data["invoice"]
        user_id = collected_data['user']
        customer_id = collected_data['customer_info']
        product_id = int(collected_data['product_ID'])
        quantity = int(collected_data['quantity'])
        price = float(collected_data['price'])
    except (KeyError, ValueError, TypeError):
        return Response({"error": "Invalid or missing data"}, status=400)

    try:
        current_user = Users.objects.get(id=user_id)
        current_customer = Customers.objects.get(id=customer_id)
        product = ProductList.objects.get(id=product_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=400)
    except Customers.DoesNotExist:
        return Response({"error": "Customer not found"}, status=400)
    except ProductList.DoesNotExist:
        return Response({"error": "Product not found"}, status=400)

    invoice_instance, created = ParentInvoice.objects.get_or_create(
        invoice=invoice_number,
        customer_info=current_customer,
        user=current_user
    )
    invoice_instance.status = 'Open'
    invoice_instance.save()
    collected_product_data = {
        'invoice': invoice_instance.id,
        'product_ID': product.id,
        'quantity': quantity,
        'price': price,
        'status': 'Available'
    }
    serializer = CollectedProductSerializer(data=collected_product_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
  
  def delete(self, request, *args, **kwargs):
    invoice = request.query_params.get('id', None)
    if invoice is None:
      return Response({"error": "Invoice is required"}, status=400)
    try:
      collected_products = CollectedProduct.objects.get(pk=invoice)
      collected_products.delete()
    except:
      return Response({"error": "Invoice not found"}, status=400)
    return Response({"message": "Invoice deleted"}, status=200)