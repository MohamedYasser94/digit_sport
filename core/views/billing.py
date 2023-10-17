import datetime
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from weasyprint import HTML
import tempfile
from core.models.billing import Billing, Invoice, Purchase, PurchaseItem
from core.models.core import CommonMediaFiles, CommonProfile
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


@authenticated_staf
@staff_only
def AdminInvoiceList(request):
    commission = None
    purchases = Purchase.objects.all()
    purchase_list = []
    for purchase in purchases:
        purchase_item = PurchaseItem.objects.filter(
            receiver_model=ContentType.objects.get(model='Purchase'), receiver_id=purchase.id)
        invoice = Invoice.objects.get(sender_model=ContentType.objects.get(model='Purchase'), sender_id=purchase.id)
        purchase_list.append(
            {"purchase": purchase, "purchase_item": purchase_item, "invoice": invoice, })

    context = {
        'purchases': purchase_list,
        'current_page': _('Purchase')

    }

    return render(request, f'{BACKEND_TEMPLATES}/store/invoice/admin.html', context)


@authenticated_staf
@staff_only
def AdminInvoiceDetails(request, slug):
    invoice = Invoice.objects.get(slug=slug)
    purchase = invoice.sender
    item_list = []
    try:
        sender_image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Clients'), owner_id=purchase.sender_id)
        sender_profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Clients'), owner_id=purchase.sender_id)
        purchase_item = PurchaseItem.objects.filter(purchase=purchase)

        for item in purchase_item:
            image = CommonMediaFiles.objects.get(type='hero',
                                                 owner_model=ContentType.objects.get(model='Products'),
                                                 owner_id=item.receiver.id)

            item_list.append(
                {"item": item, "image": image, })

    except Exception as e:
       
        sender_image = None
        sender_profile = None

    receiver = invoice.receiver



    context = {
        'invoice': invoice,
        'purchase': purchase,
        'sender_image': sender_image,
        'sender_profile': sender_profile,
        'receiver': receiver,
        'item_list': item_list,
        'current_page': _('Invoice')

    }

    return render(request, f'{BACKEND_TEMPLATES}/payment/invoice/details.html', context)

@authenticated_staf
@staff_only
def AdminInvoicePDF(request, slug):
    invoice = Invoice.objects.get(slug=slug)
    purchase = invoice.sender
    try:
        sender_image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Clients'), owner_id=purchase.sender_id)
        sender_profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Clients'), owner_id=purchase.sender_id)

    except Exception as e:
       
        sender_image = None
        sender_profile = None

    receiver = invoice.receiver
    purchase_item = PurchaseItem.objects.filter(purchase=purchase)
    item_list=[]
    for item in purchase_item:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='Products'),
                                             owner_id=item.receiver.id)
        item_list.append(
            {"item": item, "image": image, })


    context = {
        'invoice': invoice,
        'purchase': purchase,
        'sender_image': sender_image,
        'sender_profile': sender_profile,
        'receiver': receiver,
        'item_list': item_list,
        'current_page': _('Invoice')

    }
    try:
           response = HttpResponse(content_type='application/pdf')
           response['Content-Disposition'] = f'inline;attachment; filename={invoice.code}-{datetime.datetime.now()}.pdf'
           response['Content-Transfer-Encoding'] = 'binary'
           html_string = render_to_string(f'{BACKEND_TEMPLATES}/store/invoice/pdf.html', context)
           html = HTML(string=html_string)
           result = html.write_pdf()
           with tempfile.NamedTemporaryFile(delete=True) as output:
               output.write(result)
               output.flush()
               output = open(output.name, 'rb')
               response.write(output.read())
               return response
    except Exception as e:
          
           return render(request, f'{BACKEND_TEMPLATES}/store/invoice/pdf.html', context)


def billing_transaction(request, owner_model, owner_id, amount,paid,file):
    try:
        billing = Billing.objects.get(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        billing.amount = amount
        billing.paid = paid
        billing.file = file
        billing.save()
    except:
        billing = Billing.objects.create(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id,
                                         amount=amount, paid=paid, file=file)

    return billing


def get_transaction(request, owner_model, owner_id):

    return Billing.objects.get(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)

def common_invoice(request,title,number,dueDate,status,notes,file,created_by,sender_model,sender_id,receiver_model,receiver_id, owner_model, owner_id,item_model,item_id):



    invoice= Invoice.objects.create(title=title,number=number,dueDate=dueDate,status=status,notes=notes,
                                    file=file,created_by=created_by,sender_model=ContentType.objects.get(model=sender_model),
                                    sender_id=sender_id,receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                    owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                    item_model=ContentType.objects.get(model=item_model),item_id=item_id)
