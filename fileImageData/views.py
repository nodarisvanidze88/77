# import os
import csv
import requests
from io import TextIOWrapper, BytesIO
from rest_framework.decorators import api_view
from .models import ProductList, Users
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import CollectedProductSerializer, CustomersSerializer
from .models import Customers

@api_view(['GET'])
def getCSVFile(request):
  dataPath = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRj1Zv9ykB5lrwq1XCmBzcrDvo0mTti_DVKWz1fYbpmKe8eG5oT6NCNHE98dfpoo0fn--3yvkRjOkI1/pub?gid=1592599252&single=true&output=csv'
  response = requests.get(dataPath)
  response.raise_for_status()
  ProductList.objects.all().delete()
  csvContent = response.text


    # Decode the ISO-8859-1 encoded content to Unicode
  decoded_content = csvContent.encode('iso-8859-1').decode('utf-8')
  print(decoded_content)

    # Create a bytes-like object from the decoded content
  csv_bytes_like = BytesIO(decoded_content.encode('utf-8'))

    # Create a CSV reader
  file = csv.DictReader(TextIOWrapper(csv_bytes_like, encoding='utf-8-sig'))

  header_items = list(file.fieldnames)
  for row in file:

    try:
      instance = ProductList(
        code = row[header_items[0]],
        id = row[header_items[1]],
        item_name = row[header_items[2]],
        category_name = row[header_items[3]],
        dimention = row[header_items[4]],
        warehouse = row[header_items[5]],
        qty_in_wh = row[header_items[6]],
        price = row[header_items[7]],
        image_urel = row[header_items[8]],
        )
      instance.save()
    except:
      resValue2 = JsonResponse({'error':'Can not Save Data'})
      return resValue2

  resValue = JsonResponse({"hello":'uploaded'})
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
      
