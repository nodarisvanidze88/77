from django.urls import path,include
from .views import getCSVFile, ProductListView, getWithoutImage, \
    getUsers, addCollectedData, CustomersList, get_without_image_list, \
    CategoryCountsAPIView, GetProductIDs, GetOneProductDetails
from rest_framework.routers import DefaultRouter

route = DefaultRouter()
route.register(r'customers',CustomersList, basename="customerList" )


urlpatterns = [
    path('test', getCSVFile, name="csvFile"),
    path('allItems', ProductListView.as_view(), name='itemlist'),
    path('withoutimages', getWithoutImage, name='withoutImages'),
    path('getusers', getUsers, name="getusers"),
    path('add_collection_data', addCollectedData, name="collectedData"),
    path('file_list',get_without_image_list, name='fileList' ),
    path('category_list', CategoryCountsAPIView.as_view(), name='category_list'),
    path('get_product_ids', GetProductIDs.as_view(), name='get_product_ids'),
    path('get_product_by_id', GetOneProductDetails.as_view(), name='get_one_product'),
]
urlpatterns += route.urls
