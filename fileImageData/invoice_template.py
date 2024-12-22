import pandas as pd
from io import BytesIO
from .models import CollectedProduct, Customers


def invoice_constructor(query):
    output = BytesIO()
    with pd.ExcelWriter(output,engine='xlsxwriter') as writer:
        workbook = writer.book
        sheet_name_start = 0
        for i in query:
            invoice_data = CollectedProduct.objects.filter(invoice__invoice=i[0])
            customer = Customers.objects.get(id=i[1])
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
            sheet_name_start += 1
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
            worksheet.merge_range('N2:Q2',f"{i[0]}",invoice_titele_format)
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
                        if len(str(data_item[col])) > 45:
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
                worksheet.merge_range(f'W{len(data)+15}:X{len(data)+15}',f'=SUM(V15:V{len(data)+14})',total_cost_format)
                    

    output.seek(0)
                
    return output