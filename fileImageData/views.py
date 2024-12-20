from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import ProductList, Users
from django.db.models import Count
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
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
        queryset = ProductList.objects.filter(qty_in_wh__gt=0)
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
      result = ProductList.objects.filter(qty_in_wh__gt=0).order_by('id').values_list('id',flat=True)
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
       
@api_view(['POST'])
def addCollectedData(request):
  if request.method == "POST":
    collected_data = request.data.get('collected_data', [])
    print(collected_data)
    invoice_number = collected_data["invoice"]
    user_id = collected_data['user']
    customer = collected_data['customer_info']
    current_user = Users.objects.get(id=user_id)
    current_customer = Customers.objects.get(id=customer)
    invoice_instance, created = ParentInvoice.objects.get_or_create(invoice=invoice_number,
                                                                    customer_info=current_customer,
                                                                    user = current_user)
    collected_data['invoice'] = invoice_instance.id
    serializer = CollectedProductSerializer(data=[collected_data], many=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

   
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
      if customer_info is None:
        return Response({"error": "Customer info is required"}, status=400)
      invoice = ParentInvoice.objects.filter(customer_info=customer_info)
      serializer = PharentInvoiceSerializer(invoice, many=True)
      return Response(serializer.data)
   
class Get_Collected_products(APIView):
   def get(self, request, *args, **kwargs):
      invoice = request.query_params.get('invoice', None)
      if invoice is None:
        return Response({"error": "Invoice is required"}, status=400)
      collected_products = CollectedProduct.objects.filter(invoice__invoice=invoice)
      serializer = CollectedProductSerializer(collected_products, many=True)
      return Response(serializer.data)