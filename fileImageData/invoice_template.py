import pandas as pd
from io import BytesIO
from .models import CollectedProduct, Customers
import datetime
import time
def invoice_constructor(query, for_mail=False):
    output = BytesIO()
    with pd.ExcelWriter(output,engine='xlsxwriter') as writer:
        workbook = writer.book
        sheet_name_start = 0
        if for_mail:
            excel_body_builder(workbook,query, sheet_name_start, for_mail=True)

        else:
            for i in query:
                excel_body_builder(workbook,i, sheet_name_start, for_mail=False)
                sheet_name_start+=1
    if for_mail:
        output.seek(0)
        return output.getvalue()
    if not for_mail:
        output.seek(0)
        return output
    
def excel_body_builder(workbook, invoice, sheet_name_start, for_mail=False):
    if for_mail:
        customer_id = invoice.customer_info.id
        invoice_id = invoice.invoice
        invoice_date = invoice.date
    else:
        customer_id = invoice[1]
        invoice_id = invoice[0]
        invoice_date = invoice[3]
    invoice_data = CollectedProduct.objects.filter(invoice__invoice=invoice_id)
    customer = Customers.objects.get(id=customer_id)
    data = []
    
    for index,item in enumerate(invoice_data,1):
        data.append(
            {'№':index,
                'შტრიხკოდი': item.product_ID.code,
                'საქონლის დასახელება': item.product_ID.item_name,
                'განზომ.': item.product_ID.dimention,
                'ფასი (ლ.)': item.price,
                'ფ.დ.%': customer.discount,
                'რაოდენობა': item.quantity,
                'თანხა': item.total,
                })
    try:
        worksheet = workbook.add_worksheet(f'{customer.customer_name}')
    except:
        worksheet = workbook.add_worksheet(f'{customer.customer_name}-{sheet_name_start}')
    worksheet.hide_gridlines(option=2) 
    header_format = workbook.add_format({'bold': True, 'font_size':9,'align':'center','border': 1 })
    first_col_format = workbook.add_format({'font_size':9,'align':'center','border': 1 ,'valign': 'vcenter'})
    bar_code_format = workbook.add_format({'font_size':9,'align':'center','border': 1,'num_format': '@','valign': 'vcenter'})
    description_format = workbook.add_format({'font_size':9,'text_wrap': True,'valign': 'vcenter','border': 1 })
    volume_format =  workbook.add_format({'font_size':9,'valign': 'vcenter','border': 1 })
    price_format = workbook.add_format({'font_size':9,'valign': 'vcenter','border': 1,'num_format':'#,##0.00'})
    discount_format = workbook.add_format({'font_size':9,'valign': 'vcenter','border': 1,'num_format':'0%'})
    quantity_format = workbook.add_format({'font_size':9,'valign': 'vcenter','border': 1,'num_format':'#,##0.0000'})
    total_format = workbook.add_format({'font_size':9,'valign': 'vcenter','border': 1,'num_format':'#,##0.00'})
    total_cost_format = workbook.add_format({'bold': True,'font_size':9,'valign': 'vcenter','num_format':'#,##0.00'})
    invoice_titele_format = workbook.add_format({'bold': True,'font_size':10})
    seler_buyer_title_format = workbook.add_format({'bold': True,'font_size':9,'align':'right'})
    seler_buyer_values_format = workbook.add_format({'text_wrap': True,'font_size':9,'align':'left'})
    blank_cell_format = workbook.add_format({'font_size':9,'align':'left','bottom': 1})
    # Set the column width.
    worksheet.set_column('A:A', 0.17)
    worksheet.set_column('B:B', 3.43)
    worksheet.set_column('C:C', 5.29)
    worksheet.set_column('D:D', 4.57)
    worksheet.set_column('E:E', 0.17)
    worksheet.set_column('F:F', 1.57)
    worksheet.set_column('G:G', 7.71)
    worksheet.set_column('H:H', 0.17)
    worksheet.set_column('I:I', 10.14)
    worksheet.set_column('J:J', 0.17)
    worksheet.set_column('K:K', 10)
    worksheet.set_column('L:L', 1.86)
    worksheet.set_column('M:M', 0.17)
    worksheet.set_column('N:N', 6.57)
    worksheet.set_column('O:O', 7.71)
    worksheet.set_column('P:P', 0.17)
    worksheet.set_column('Q:Q', 2.29)
    worksheet.set_column('R:R', 5.29)
    worksheet.set_column('S:S', 1.86)
    worksheet.set_column('T:T', 8.43)
    worksheet.set_column('U:U', 1.43)
    worksheet.set_column('V:V', 0.17)
    worksheet.set_column('W:W', 10.57)
    worksheet.set_column('X:X', 0.17)
    worksheet.set_column('Y:Y', 0.58)
    worksheet.set_row(0,2.25)
    worksheet.merge_range('H2:L2','წინასწარი ინვოისი №',invoice_titele_format)
    worksheet.merge_range('N2:Q2',f"{invoice_id}",invoice_titele_format)
    worksheet.set_row(2, 1)
    worksheet.set_row(3, 1)
    worksheet.set_row(5, 3.75)
    worksheet.merge_range('A7:D7','გამყიდველი:',seler_buyer_title_format)
    worksheet.merge_range('N7:O7','მყიდველი:',seler_buyer_title_format)
    invoice_detail_names = ["საიდ. კოდი:","მისამართი:",
                            "ბანკი:","საბანკო კოდი:","ანგარიშის №"]
    invoice_values_names = ["შპს ბლექსი ინვესტი",
                            "404883122",
                            "ბათუმი ლერმონტოვის 112, ჩიხი 7",
                            "საქართველოს ბანკი",
                            "",
                            "GE83BG0000000887100400"]					

    for name_i, name in enumerate(invoice_detail_names,8): 
        worksheet.merge_range(f'A{name_i}:D{name_i}',name,seler_buyer_title_format)
        worksheet.merge_range(f'N{name_i}:O{name_i}',name,seler_buyer_title_format)
    for name_i, name in enumerate(invoice_values_names,7): 
        worksheet.merge_range(f'F{name_i}:L{name_i}',name, seler_buyer_values_format)
    worksheet.merge_range(f'Q7:Y7', customer.customer_name, seler_buyer_values_format)
    worksheet.merge_range(f'Q8:Y8', customer.identification, seler_buyer_values_format)
    worksheet.merge_range(f'Q9:Y9', customer.customer_address, seler_buyer_values_format)
    worksheet.set_row(12, 2.25)
    start_col = ['A','C','G','L','O','R','T','V']
    end_col = ['B','F','K','N','Q','S','U','W']
    col_names = ['№',
                'შტრიხკოდი',
                'საქონლის დასახელება',
                'განზომ.',
                'ფასი (ლ.)',
                'ფ.დ.%',
                'რაოდენობა',
                'თანხა',
    ]
    if data:
        for st,nd,it in zip(start_col,end_col,data[0]):
            worksheet.merge_range(f'{st}14:{nd}14', it, header_format)
        
        for ind,data_item in enumerate(data,15):
            for st,nd,col in zip(start_col,end_col,col_names):
                if len(str(data_item[col])) > 35:
                    worksheet.set_row(ind-1,25)
                if col =='№':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], first_col_format)
                elif col == 'შტრიხკოდი':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], bar_code_format)
                elif col == 'საქონლის დასახელება':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], description_format)
                elif col == 'განზომ.': 
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], volume_format)
                elif col == 'ფასი (ლ.)':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], price_format)
                elif col == 'ფ.დ.%':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], discount_format)
                elif col == 'რაოდენობა':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], quantity_format)
                elif col == 'თანხა':
                    worksheet.merge_range(f'{st}{ind}:{nd}{ind}', data_item[col], total_format)
    last_row = len(data)+15
    worksheet.merge_range(f'W{last_row}:X{last_row}',f'=SUM(V15:V{last_row-1})',total_cost_format)
    worksheet.set_row(last_row, 27)
    worksheet.set_row(last_row+1, 2.25)   
    worksheet.merge_range(f'A{last_row+3}:C{last_row+3}','შენიშვნა',seler_buyer_title_format)
    worksheet.merge_range(f'D{last_row+3}:W{last_row+3}','',blank_cell_format)
    worksheet.set_row(last_row+4, 2.25) 
    worksheet.set_row(last_row+5, 2.25)
    worksheet.merge_range(f'A{last_row+7}:G{last_row+7}','სულ გადმოსარიცხი თანხა',seler_buyer_title_format) 
    worksheet.merge_range(f'K{last_row+7}:W{last_row+7}','',seler_buyer_values_format)
    worksheet.set_row(last_row+8, 2.25)
    worksheet.merge_range(f'A{last_row+8}:G{last_row+8}','ინვოისი ძალაშია:',seler_buyer_title_format) 
    worksheet.write(f'I{last_row+8}','',blank_cell_format)
    worksheet.merge_range(f'K{last_row+8}:N{last_row+8}','დღის განმავლობაში',workbook.add_format({'bold':True,'font_size':9,'align':'left'}))
    worksheet.set_row(last_row+9, 2.25)
    worksheet.set_row(last_row+10, 9.25)
    worksheet.merge_range(f'F{last_row+12}:L{last_row+12}','გამყიდველი',workbook.add_format({'bold':True,'font_size':9,'align':'center'}))
    worksheet.merge_range(f'Q{last_row+12}:Y{last_row+12}','მყიდველი',workbook.add_format({'bold':True,'font_size':9,'align':'center'}))
    worksheet.merge_range(f'F{last_row+14}:L{last_row+14}','',blank_cell_format)
    worksheet.merge_range(f'Q{last_row+14}:Y{last_row+14}','',blank_cell_format)
    worksheet.set_row(last_row+15, 2.25)
    worksheet.set_row(last_row+16, 8.25)
    worksheet.merge_range(f"Q{last_row+18}:Y{last_row+18}",f"{datetime.datetime.strftime(invoice_date,'%Y-%m-%d %H:%M')}",workbook.add_format({'bold':True,'font_size':9,'align':'center','num_format': 'yyyy-mm-dd hh:mm'}))
