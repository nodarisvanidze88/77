from rest_framework.decorators import api_view
from .models import ProductList, Users
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import CollectedProductSerializer, CustomersSerializer
from .models import Customers, Product_Category
from .new_data import get_CSV_File_content

@api_view(['GET'])
def getCSVFile(request):
  file = get_CSV_File_content()
  print(file)
  header_items = list(file.fieldnames)
  file_ids = set()
  for row in file:
    print(row[header_items[1]])
    file_ids.add(row[header_items[1]])
    category, created = Product_Category.objects.get_or_create(category_name=row[header_items[3]])
    ProductList.objects.update_or_create(
                id=row[header_items[1]],
                defaults={
                    'code': row[header_items[0]],
                    'item_name': row[header_items[2]],
                    'category_name': category,
                    'dimention': row[header_items[4]],
                    'warehouse': row[header_items[5]],
                    'qty_in_wh': row[header_items[6]],
                    'price': row[header_items[7]],
                    'image_urel': f"https://storage.googleapis.com/nodari/{row[header_items[1]]}.jpg"
                }
              )
  ProductList.objects.exclude(id__in=file_ids).update(qty_in_wh=0)
  resValue = JsonResponse({"message": 'Upload complete.'})
  return resValue

@api_view(['GET'])
def getItemsList(request):
    if request.method=='GET':
        items = ProductList.objects.all()
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
  
@api_view(['POST'])
def addCollectedData(request):
   if request.method=="POST":
      collected_data = request.data.get('collected_data',[])

      serializer = CollectedProductSerializer(data=collected_data, many=True)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data, status=201)
      else:
         print(serializer.errors)
      return Response(serializer.errors, status=400)
   
class CustomersList(viewsets.ModelViewSet):
  queryset = Customers.objects.all()
  serializer_class = CustomersSerializer
      
