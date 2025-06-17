import csv
import datetime
import tempfile
import xlwt
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.template.loader import render_to_string


from helper.decorators import authenticated_staf, staff_only


@authenticated_staf
@staff_only
def export_model(request):
    format = request.POST.get('format')
    print(format)
    # model_name = request.META['HTTP_REFERER'].split('/')[-2]
    # print('model_name', model_name)
    # model_info = ContentType.objects.filter(app_label='core', model=model_name)
    # print('model_info', model_info)
    # model = model_info.first().model_class()
    request_model =request.POST.get('request_model')
    model = ContentType.objects.get(model=request_model)
    print('model', model)
    model = model.model_class()
    model_name = model.__name__
    print('model', model)
    print('model_name', model_name)

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename= {request_model}{datetime.datetime.now()}.csv'
        writer = csv.writer(response)
        try:
            writer.writerow([f.name for f in model._meta.get_fields()])
            for obj in model.objects.all():
                writer.writerow([obj.__getattribute__(f.name) for f in model._meta.get_fields()])
        except Exception as e:
            print('e', e)
            writer.writerow([f.title for f in model._meta.get_fields()])
            for obj in model.objects.all():
                writer.writerow([obj.__getattribute__(f.title) for f in model._meta.get_fields()])
        return response


    elif format == 'excel':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename= {request_model}{datetime.datetime.now()}.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet(request_model)
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        try:
              columns = [f.title for f in model._meta.get_fields()]
        except Exception as e:
                columns = [f.name for f in model._meta.get_fields()]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        rows = model.objects.all().values_list(*columns)
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)
        return response
    elif format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline;attachment; filename={request_model}{datetime.datetime.now()}.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        html_string = render_to_string('good/common/pdf.html', {'model': model, 'total': 0})
        html = HTML(string=html_string)
        result = html.write_pdf()
        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output=open(output.name,'rb')
            response.write(output.read())
            return response

    return HttpResponse('Not supported')