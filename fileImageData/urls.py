from django.urls import path,include
from django.contrib import admin
from .views import getCSVFile, ProductListView, getWithoutImage, \
    getUsers, CustomersList, get_without_image_list, \
    CategoryCountsAPIView, GetProductIDs, GetOneProductDetails, Get_pharent_invoice, Collected_products_viewset, admin_download_file
from rest_framework.routers import DefaultRouter

route = DefaultRouter()
route.register(r'customers',CustomersList, basename="customerList" )


urlpatterns = [
    path('test', getCSVFile, name="csvFile"),
    path('allItems', ProductListView.as_view(), name='itemlist'),
    path('withoutimages', getWithoutImage, name='withoutImages'),
    path('getusers', getUsers, name="getusers"),
    path('file_list',get_without_image_list, name='fileList' ),
    path('category_list', CategoryCountsAPIView.as_view(), name='category_list'),
    path('get_product_ids', GetProductIDs.as_view(), name='get_product_ids'),
    path('get_product_by_id', GetOneProductDetails.as_view(), name='get_one_product'),
    path('get_invoice_list', Get_pharent_invoice.as_view(), name='get_invoice_list'),
    path('collected_products', Collected_products_viewset.as_view(), name='collected_products'),
    # in admin.py get_urls:
    path('download-file/', admin.site.admin_view(admin_download_file), name='admin-download-file'),

    ]

urlpatterns += route.urls
