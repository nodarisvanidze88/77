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
from .models import Customers, Product_Category, MissingPhoto, ParentInvoice, CollectedProduct, ProductList
from .new_data import get_CSV_File_content
from .storage_content import list_files_in_bucket
import os
import tempfile
import subprocess
from django.http import HttpResponse, Http404
from django.conf import settings
from google.cloud import storage
from django.contrib import messages
from django.shortcuts import render, redirect

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
        product_id = collected_data['product_ID']
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
  

def download_images_by_category_view(request):
    """
    1) For each category, fetch the corresponding product images from GCS
    2) Download to local temp folder
    3) Create a rar archive per category, splitting into 200 MB parts
    4) Show links to the resulting .rar archives so the user can download them
    """

    # -------------
    # Safety Check
    # -------------
    if not request.user.is_superuser:
        messages.error(request, "You must be a superuser to download images.")
        return redirect('admin:app_product_category_changelist')
    
    # -------------
    # Google Client
    # -------------
    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = client.bucket("nodari")  # define your BUCKET name in settings

    # -------------
    # Prepare a temp directory to hold images & archives
    # -------------
    temp_root = tempfile.mkdtemp()  # e.g. /tmp/tmpab12def
    download_links = []  # We'll store (category_name, archive_paths)

    # -------------
    # Process each category
    # -------------
    all_categories = Product_Category.objects.all()
    for category in all_categories:
        # 1) Get all products for this category
        products = ProductList.objects.filter(category_name=category)
        if not products.exists():
            continue
        
        category_temp_dir = os.path.join(temp_root, category.category_name.replace(" ", "_"))
        os.makedirs(category_temp_dir, exist_ok=True)

        # 2) For each product, see if there's an image in GCS that matches product.id
        for product in products:
            if not product.image_urel:
                continue
            
            # The bucket file name is presumably your product ID + extension,
            # or maybe you have to parse product.image_urel to get the actual path in GCS
            # We'll assume the product.image_urel is something like 
            # "https://storage.googleapis.com/BUCKET_NAME/<FILENAME>"
            # so we parse out the <FILENAME>.
            # For example, if you need something else, adjust accordingly.
            
            blob_name = product.image_urel.split('/')[-1]  # last part
            blob = bucket.blob(blob_name)
            if blob.exists():
                local_file_path = os.path.join(category_temp_dir, blob_name)
                blob.download_to_filename(local_file_path)
        
        # 3) RAR the entire category folder, splitting into 200MB volumes
        # rar a -v200m /path/to/archive.rar /path/to/category_temp_dir/*
        # By default, rar will produce something like:
        #   archive.part1.rar, archive.part2.rar, ...
        archive_name = f"{category.category_name.replace(' ', '_')}.rar"
        archive_full_path = os.path.join(category_temp_dir, archive_name)

        # If rar is installed, run a subprocess
        # This will create splitted archives if needed:
        #     e.g. archive.part1.rar, archive.part2.rar ...
        try:
            subprocess.run(
                [
                    r"C:\Program Files\WinRAR\WinRAR.exe", "a", "-v200m",  # split volumes at 200MB
                    archive_full_path,
                    os.path.join(category_temp_dir, "*")
                ],
                check=True
            )
            # Now we might have .rar, .part1.rar, .part2.rar, etc.
            
            # Let's collect all .rar files in the category_temp_dir
            rar_files = [
                f for f in os.listdir(category_temp_dir) 
                if f.endswith(".rar") or ".part" in f
            ]
            # Convert them to absolute paths
            rar_paths = [os.path.join(category_temp_dir, rf) for rf in rar_files]
            download_links.append((category.category_name, rar_paths))

        except subprocess.CalledProcessError as e:
            messages.error(request, f"Error compressing category {category.category_name}: {e}")
            continue

    # -------------
    # Render a page that lists links to each RAR file
    # -------------
    # Because the archives might be quite large, you usually do not want to
    # stream them from memory. Instead, you can serve them via a Django view
    # that streams from disk (or re-upload them to the bucket for re-download).
    #
    # For simplicity, let's store them in a globally accessible 'temp'
    # folder, then generate direct links. In production, you'd want a
    # more robust solution (like storing them in a dedicated place, or in GCS).
    #
    # We'll just show them in a template with links to a separate "download_file" view.
    #
    # E.g. /admin/app/download-file/?path=<path>
    #
    return render(request, "admin/download_images.html", {
        "download_links": download_links
    })

import mimetypes
from wsgiref.util import FileWrapper
from django.utils.encoding import smart_str
from django.shortcuts import redirect
from django.http import FileResponse

def admin_download_file(request):
    requested_path = request.GET.get("path", "")
    # Optionally verify that 'requested_path' is within your temp_root
    
    if not os.path.exists(requested_path):
        raise Http404("File not found.")
    
    file_name = os.path.basename(requested_path)
    file_wrapper = FileWrapper(open(requested_path, 'rb'))
    file_mime_type, _ = mimetypes.guess_type(requested_path)
    response = FileResponse(file_wrapper, content_type=file_mime_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response
