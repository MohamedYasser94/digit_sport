import datetime
import tempfile

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from weasyprint import HTML

from apps.catalog.models.models import Products, ProductVariants, ProductsStock
from apps.catalog.models.vendor import Warehouse
from core.forms.purchase import AdminPurchaseForm, AdminPurchaseItemForm, AdminInvoiceForm
from core.models.billing import Purchase, PurchaseItem, Invoice

from core.models.core import CommonProfile, CommonMediaFiles
from core.models.people import Clients
from core.models.shop import Order, OrderItem
from core.models.transaction import ProductTransaction

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


@authenticated_staf
@staff_only
def AdminCatalogPurchaseList(request):
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

    return render(request, f'{BACKEND_TEMPLATES}/store/purchase/admin.html', context)


@authenticated_staf
@staff_only
def AdminCatalogPurchaseCreate(request):
    invoice_create = Invoice.objects.get_or_create(title='Purchase Create')
    invoice = Invoice.objects.get(title='Purchase Create')
    if request.method == "POST":

        purchase_form = AdminPurchaseForm(request.POST or None, request.FILES or None)
        item_form = AdminPurchaseItemForm(request.POST or None, request.FILES or None)
        invoice_form = AdminInvoiceForm(request.POST or None, request.FILES or None)
        if item_form:
            print(2)
            client = request.POST.get('people')
            warehouse = request.POST.get('warehouse')
            purchase_status = request.POST.get('purchase_status')
            payment_status = request.POST.get('payment_status')
            amount = request.POST.get('amount')
            paid = request.POST.get('paid')
            due = request.POST.get('due')
            status = request.POST.get('status')
            invoice_file = request.FILES.get('invoice_file')

            product_title = request.POST.getlist("product_title")
            code = request.POST.getlist('code')
            quantity = request.POST.getlist('quantity')
            received = request.POST.getlist('new_quantity')
            current_price = request.POST.getlist('current_price')
            purchase_price = request.POST.getlist('new_price')
            sale_price = request.POST.getlist('new_sale_price')
            total = request.POST.get('total')
            notes = request.POST.get('notes')


            try:
                invoice_date = request.POST.get('invoice_date')
                invoice_date = datetime.datetime.strptime(invoice_date, '%d, %b %Y')
                invoice_date = invoice_date.strftime("%Y-%m-%d")
            except Exception as e:
                invoice_date = datetime.datetime.now()
            try:
                invoice_due_date = request.POST.get('invoice_due_date')
                invoice_due_date = datetime.datetime.strptime(invoice_due_date, '%d, %b %Y')
                invoice_due_date = invoice_due_date.strftime("%Y-%m-%d")
            except Exception as e:
                invoice_due_date = None

            try:
                client = Clients.objects.get(id=client)

            except Exception as e:
                client = Clients.objects.get_or_create(name='No Client')
                client = Clients.objects.get(name='No Client')

                # messages.error(request, _(f"Some Data Is Missing ,{e}, Please Try Again"), extra_tags='Purchase')
                # return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogPurchaseCreate'))
            warehouse = Warehouse.objects.get(id=warehouse)

            user = request.user.id
            seller = User.objects.get(id=user)
            print('seller', 55)
            purchase_object = Purchase(sender_model=ContentType.objects.get(model='Clients'), sender_id=client.id,
                                     receiver_model=ContentType.objects.get(model='User'), receiver_id=user,
                                     warehouse=warehouse, purchase_status=purchase_status,
                                     payment_status=payment_status,
                                     amount=amount, paid=paid, due=due, status=status, purchase_date=invoice_date,
                                     due_date=invoice_due_date)

            purchase_object.save()
            invoice_object = Invoice.objects.get(code=invoice.code)
            invoice_object.sender_model = ContentType.objects.get(model='Purchase')
            invoice_object.sender_id = purchase_object.id
            invoice_object.receiver_model = ContentType.objects.get(model='warehouse')
            invoice_object.receiver_id = warehouse.id
            invoice_object.title = f'Purchase From :{client.name} To :{warehouse.name}'
            invoice_object.dueDate = invoice_due_date
            invoice_object.status = purchase_status
            invoice_object.notes = notes
            invoice_object.save()
            a = 0
            for product in product_title:
                product_object = Products.objects.get(code=code[a])
                print('product_object', product_object)
                print('float(received[a]', float(received[a]))
                print('purchase_price[a]',float(purchase_price[a]))
                product_object.quantity += int(received[a])
                product_object.purchase_price = purchase_price[a]
                product_object.sale_price = sale_price[a]
                product_object.save()
                received_float = float(received[a])
                purchase_float = float(purchase_price[a])
                amount = received_float * purchase_float
                print('product total ', total)
                stock_object = ProductsStock(sender_model=ContentType.objects.get(model='Purchase'), sender_id=purchase_object.id,
                                                receiver_model=ContentType.objects.get(model='Warehouse'),receiver_id=warehouse.id,
                                             owner_model=ContentType.objects.get(model='Products'), owner_id=product_object.id,
                                              title=product_object.title, sku=product_object.sku,
                                              purchase_price=purchase_price[a],sale_price = sale_price[a],final_price=sale_price[a],
                                             quantity=received[a],)
                stock_object.save()

                item_form = PurchaseItem(receiver_model=ContentType.objects.get(model='Warehouse'),
                                         receiver_id=warehouse.id,
                                         item_model=ContentType.objects.get(model='Products'), item_id=product_object.id,
                                         purchase=purchase_object, price=purchase_price[a], quantity=received[a],
                                         amount=amount, name=product)
                item_form.save()
                a = a + 1
                z = 0
            messages.success(request,
                             _("Purchase Add Successfully"), extra_tags='Purchase')
            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogPurchaseList'))
        else:
          
            
            messages.error(request, _("Purchase Not Add , Please Try Again"), extra_tags='Purchase')
    else:
        purchase_form = AdminPurchaseForm()
        item_form = AdminPurchaseItemForm()

        context = {
            'invoice': invoice,
            'purchase_form': purchase_form,
            'item_form': item_form,
            'current_page': _('Add'),
            'prev_Page': _('Purchase'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogPurchaseList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/store/purchase/add.html', context)

    context = {
        'invoice': invoice,
        'purchase_form': purchase_form,
        'item_form': item_form,
        'current_page': _('Add'),
        'prev_Page': _('Purchase'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogPurchaseList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/store/purchase/add.html', context)


@authenticated_staf
@staff_only
def AdminCatalogPurchaseUpdate(request, slug):
    if request.method == "POST":
        
       
        purchase_form = AdminPurchaseForm(request.POST or None, request.FILES or None)
        item_form = AdminPurchaseItemForm(request.POST or None, request.FILES or None)
        if item_form.is_valid():
            print(2)
            client = request.POST.get('people')
            warehouse = request.POST.get('warehouse')
            purchase_status = request.POST.get('purchase_status')
            payment_status = request.POST.get('payment_status')
            amount = request.POST.get('amount')
            paid = request.POST.get('paid')
            due = request.POST.get('due')
            status = request.POST.get('status')
            invoice = request.FILES.get('invoice')
            invoice_date = request.POST.get('invoice_date')
            cr_date = datetime.datetime.strptime(invoice_date, '%d, %b %Y')
            invoice_date = cr_date.strftime("%Y-%m-%d")
            invoice_due_date = request.POST.get('invoice_due_date')
            cr_date = datetime.datetime.strptime(invoice_due_date, '%d, %b %Y')
            invoice_due_date = cr_date.strftime("%Y-%m-%d")

            print(3)
            product_title = request.POST.getlist("product_title")
            code = request.POST.getlist('code')
            print(4)
            quantity = request.POST.getlist('gradeko')
            received = request.POST.getlist('received')
            current_price = request.POST.getlist('current_price')
            purchase_price = request.POST.getlist('purchase_price')
            sale_price = request.POST.getlist('sale_price')
            total = request.POST.get('total')

            client = Clients.objects.get(id=client)
            warehouse = Warehouse.objects.get(id=warehouse)

            user = request.user.id
            seller = User.objects.get(id=user)
            print('seller', 55)
            purchase_form = Purchase(sender_model=ContentType.objects.get(model='Clients'), sender_id=client.id,
                                     receiver_model=ContentType.objects.get(model='User'), receiver_id=user,
                                     warehouse=warehouse, purchase_status=purchase_status,
                                     payment_status=payment_status,
                                     amount=amount, paid=paid, due=due, status=status, purchase_date=invoice_date,
                                     due_date=invoice_due_date)

            purchase_form.save()
            a = 0
            for product in product_title:
                product_id = Products.objects.get(code=code[a])
                print('product_id', product_id)
                print('purchase_price', purchase_price)
                total = product_id.quantity + int(received[a])
                product_id.quantity += total
                print('product total ', total)

                item_form = PurchaseItem(receiver_model=ContentType.objects.get(model='Warehouse'),
                                         receiver_id=warehouse.id,
                                         item_model=ContentType.objects.get(model='Products'), item_id=product_id.id,
                                         purchase=purchase_form, price=purchase_price[a], quantity=received[a],
                                         amount=total, name=product)
                item_form.save()
                a = a + 1
            messages.success(request,
                             _("Purchase Add Successfully"), extra_tags='Purchase')
            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogPurchaseList'))
        else:
          
            
            messages.error(request, _("Purchase Not Add , Please Try Again"), extra_tags='Purchase')
    else:
        purchase_form = AdminPurchaseForm()
        item_form = AdminPurchaseItemForm()

        context = {
            'purchase_form': purchase_form,
            'item_form': item_form,
            'current_page': _('Add'),
            'prev_Page': _('Purchase'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogPurchaseList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/store/purchase/add.html', context)

    context = {
        'purchase_form': purchase_form,
        'item_form': item_form,
        'current_page': _('Add'),
        'prev_Page': _('Purchase'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogPurchaseList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/store/purchase/add.html', context)


@authenticated_staf
@staff_only
def AdminCatalogInvoiceList(request):
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
def AdminCatalogInvoiceDetails(request, slug):
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
        try:
            image = CommonMediaFiles.objects.get(type='hero',
                                                 owner_model=ContentType.objects.get(model='Products'),
                                                 owner_id=item.receiver.id)
        except Exception as e:
            image = None

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

    return render(request, f'{BACKEND_TEMPLATES}/store/invoice/details.html', context)

@authenticated_staf
@staff_only
def AdminCatalogInvoicePDF(request, slug):
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








@login_required(login_url='/dashboard/login')
def OrdersDetails(request, slug):
    order = Order.objects.get(slug=slug)
    order_item = OrderItem.objects.filter(order=order)
    customer_profile = CommonProfile.objects.get(customer=order.customer)
    transaction = ProductTransaction.objects.get(order=order)

    context = {
        'order': order,
        'order_item': order_item,
        'customer_profile': customer_profile,
        'transaction': transaction,

    }
    return render(request, 'order/orders/details.html', context)
