import openpyxl
from .models import ProductList, CollectedProduct, Customers
from django.http import HttpResponse
from .invoice_template import invoice_constructor
def get_excel_file(query=None):
    if query == None:
        return None
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Missing_Photo'
    product_model = ProductList
    field_names= [field.name for field in product_model._meta.fields]
    ws.append(field_names)

    for missing_photo in query:
        product = missing_photo.product
        row = []
        for field in field_names:
            value = getattr(product,field)
            if product_model._meta.get_field(field).is_relation:
                value = str(value) if value else ''
            row.append(value)
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=missing_photos.xlsx'
    wb.save(response)
    return response

def get_invoice_excel(query=None):
    if query == None:
        return None
    
    output = invoice_constructor(query)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=invoices.xlsx'
    return response
