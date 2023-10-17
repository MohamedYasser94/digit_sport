from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView

from apps.catalog.forms.forms import AdminCatalogCategoryForm, AdminCatalogProductForm, AdminCatalogVariantsForm, \
    AdminCatalogProductVariantsForm, AdminCatalogManufacturerForm, AdminCatalogUnitConversionForm
from apps.catalog.models.models import Categories, Manufacturer, Products, Variants, ProductManufacturing, \
    ProductVariants, ProductsStock, UnitConversion
from apps.catalog.models.vendor import Warehouse, Vendor

from core.forms.core import AdminCommonTranslateForm
from core.models.Shipping import CommissionCategory
from core.models.core import CommonTranslate

from core.views.core import AdminCommonTranslate, AdminCommonSeo, AdminCommonMediaHeroFiles, AdminCommonMediaVideoFiles, \
    AdminCommonMediaImagesFiles
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only, superuser_only

User = get_user_model()


##########################      Blog Category Admin            ################################

@authenticated_staf
@staff_only
def AdminCatalogCategoriesList(request):
    categories = Categories.objects.all()
    categories_list = []
    for category in categories:
        translate = CommonTranslate.objects.get(
            owner_model=ContentType.objects.get(model='Categories'), owner_id=category.id)

        categories_list.append(
            {"category": category, "translate": translate, })

    if request.method == "POST":
        print(2)

        category_form = AdminCatalogCategoryForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if category_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            try:
                parent_id = Categories.objects.get(id=parent)
            except Exception as e:

                parent_id = None

            category_form = Categories(title=title, keyword=keyword, parent=parent_id, status=status
                                       , image=image)
            category_form.save()

            translate = CommonTranslate(title=title_tr, keyword=keyword_tr,
                                        owner_model=ContentType.objects.get(model='Categories'),
                                        owner_id=category_form.id)
            translate.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogCategoriesList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')

    else:
        context = {
            'categories': categories_list,
            'category_form': AdminCatalogCategoryForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Categories')

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/category/admin.html', context)
    context = {
        'categories': categories,
        'category_form': AdminCatalogCategoryForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/category/admin.html', context)


def AdminCatalogCategoriesDetail(request, slug):
    category = Categories.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='Categories'), owner_id=category.id)

    context = {
        'category': category,
        'translate': translate,
        'current_page': _('Categories'),
        'prev_Page': _('Categories'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogCategoriesList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/category/detail.html', context)


@authenticated_staf
@staff_only
def AdminCatalogCategoriesUpdate(request, slug):
    category = Categories.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='Categories'), owner_id=category.id)

    if request.method == "POST":
        category_form = AdminCatalogCategoryForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if category_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            if parent == '' or parent == "''" or parent == None:
                parent_id = None
            else:
                parent_id = Categories.objects.get(id=parent)
            category_object = Categories.objects.get(id=category.id)
            category_object.title = title
            category_object.keyword = keyword
            category_object.parent = parent_id
            category_object.status = status
            category_object.image = image
            category_object.save()
            translate = CommonTranslate.objects.get(
                owner_model=ContentType.objects.get(model='Categories'),
                owner_id=category_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogCategoriesList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')
    else:
        context = {
            'category': category,
            'translate': translate,
            'category_form': AdminCatalogCategoryForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Update'),
            'prev_Page': _('Categories'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogCategoriesList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/category/update.html', context)

    context = {
        'category': category,
        'translate': translate,
        'category_form': AdminCatalogCategoryForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Update'),
        'prev_Page': _('Categories'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogCategoriesList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/category/update.html', context)


@authenticated_staf
@staff_only
def AdminCatalogCategoriesDelete(request, slug):
    category = Categories.objects.get(slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogCategoriesList'))


##########################      Catalog Product Admin            ################################


@authenticated_staf
@staff_only
def AdminCatalogProductList(request):
    products = Products.objects.all()
    context = {
        'products': products,
        'current_page': _('Products')

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/product/admin.html', context)






@authenticated_staf
@staff_only
def AdminCatalogProductCreate(request):
    manufacturer = Manufacturer.objects.all()
    relates = Products.objects.all()
    variants = Variants.objects.all()
    warehouses = Warehouse.objects.all()
    attributes_group = request.GET.get('attributes_group')
    try:
        # vendor = Vendor.objects.get(vendor=request.user.id)
        if request.method == "POST":

            product_form = AdminCatalogProductForm(request.POST or None, request.FILES or None)
            variant_form = AdminCatalogVariantsForm(request.POST or None, request.FILES or None)
            variant_product_form = AdminCatalogProductVariantsForm(request.POST or None, request.FILES or None)
            translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)

            if product_form:
                category = product_form.cleaned_data['category']
                warehouse_id = request.POST.get('warehouse')
                title = product_form.cleaned_data['title']
                unit = product_form.cleaned_data['unit']
                for_sale = product_form.cleaned_data['for_sale']
                body = request.POST.get('body')
                keyword = product_form.cleaned_data['keyword']
                model = product_form.cleaned_data['model']
                brand = product_form.cleaned_data['brand']
                sku = product_form.cleaned_data['sku']
                purchase_price = product_form.cleaned_data['purchase_price']
                sale_price = product_form.cleaned_data['sale_price']
                discount_price = product_form.cleaned_data['discount_price']
                discount_active = product_form.cleaned_data['discount_active']
                quantity = product_form.cleaned_data['quantity']
                out_of_stock_status = product_form.cleaned_data['out_of_stock_status']
                requires_shipping = product_form.cleaned_data['requires_shipping']
                weight = product_form.cleaned_data['weight']
                width = product_form.cleaned_data['width']
                height = product_form.cleaned_data['height']
                length = product_form.cleaned_data['length']
                status = product_form.cleaned_data['status']
                featured = product_form.cleaned_data['featured']
                sort_order = product_form.cleaned_data['sort_order']
                manufacturer_id = request.POST.get('manufacturer')
                title_tr = request.POST.get('title_tr')
                keyword_tr = request.POST.get('keyword_tr')
                body_tr = request.POST.get('body_tr')
                #############  manufacturing ############################
                manufacturing_product = request.POST.getlist('manufacturing_product')
                manufacturing_code = request.POST.getlist('manufacturing_code')
                manufacturing_quantity = request.POST.getlist('manufacturing_quantity')
                manufacturing_unit = request.POST.getlist('manufacturing_unit')
                manufacturing_price = request.POST.getlist('manufacturing_price')
                manufacturing_estimated = request.POST.getlist('manufacturing_estimated')
                manufacturing_sale = request.POST.getlist('manufacturing_sale')

                #############  variant ############################
                variant_title = request.POST.getlist('variant_title')
                # variant = product_form.cleaned_data['variant']
                variant_color = request.POST.getlist('variant_color')
                variant_size = request.POST.getlist('variant_size')
                variant_quantity = request.POST.getlist('variant_quantity')
                variant_images = request.FILES.getlist('variant_images')
                purchase_Variant = request.POST.getlist('purchase_Variant')
                sale_Variant = request.POST.getlist('sale_Variant')
                category = Categories.objects.get(title=category)
                hero_image = request.FILES.get('hero_image')
                images = request.FILES.getlist('images')
                image_url = request.POST.getlist('image_url')
                video_url = request.POST.get('video_url')
                video_cover = request.FILES.get('video_cover')
                ########## Seo #########
                meta_title = request.POST.get('meta_title')
                if meta_title != '' or None:
                    meta_title = meta_title
                else:
                    meta_title = title

                meta_description = request.POST.get('meta_description')
                if meta_description != '' or None:
                    meta_description = meta_description
                else:
                    meta_description = title
                meta_keywords = request.POST.get('meta_keywords')
                if meta_keywords != '' or None:
                    meta_keywords = meta_keywords
                else:
                    meta_keywords = title
                seo_image = request.FILES.get('seo_image')
                if seo_image != '' or seo_image:
                    seo_image = seo_image
                else:
                    seo_image = hero_image

                author = User.objects.get(id=request.user.id)
                try:
                    manufacturer = Manufacturer.objects.get(id=manufacturer_id)
                except:
                    manufacturer = None
                if discount_active == 'Active':
                    final_price = discount_price
                else:
                    final_price = sale_price
                unit = Variants.objects.get(code=unit)
                warehouse = Warehouse.objects.get(id=warehouse_id)
                print('warehouse', warehouse)
                product_form = None
                if not product_form:
                    print(2)

                    product_form = Products(owner_model=ContentType.objects.get(model='Warehouse'),
                                            owner_id=warehouse.id,
                                            category=category, title=title, keyword=keyword, body=body,
                                            model=model, brand=brand, sku=sku, unit=unit, for_sale=for_sale,
                                            purchase_price=purchase_price, sale_price=sale_price,
                                            discount_active=discount_active, discount_price=discount_price,
                                            final_price=final_price, quantity=quantity,
                                            out_of_stock_status=out_of_stock_status,
                                            requires_shipping=requires_shipping,
                                            weight=weight, length=length, height=height, width=width,
                                            manufacturer=manufacturer, featured=featured, status=status,
                                            sort_order=sort_order)

                    product_form.save()

                    AdminCommonTranslate(request, title_tr, keyword_tr, body_tr, 'Products', product_form.id)
                    AdminCommonSeo(request, meta_title, meta_description, meta_keywords, author, seo_image,
                                   'Products', product_form.id)
                    AdminCommonMediaHeroFiles(request, hero_image, 'Products', product_form.id)
                    AdminCommonMediaVideoFiles(request, video_url, video_cover, 'Products', product_form.id)
                    print('product_form', product_form)
                    try:
                        a = 0
                        for product in manufacturing_code:
                            print('product', product)
                            product = Products.objects.get(code=product)
                            unit = Variants.objects.get(code=manufacturing_unit[a])
                            manufacturing_object = ProductManufacturing(product=product_form, ore=product.id, unit=unit,
                                                                        ore_price=manufacturing_price[a],
                                                                        quantity=manufacturing_quantity[a], )
                            manufacturing_object.save()
                            a += 1
                            print('manufacturing_object', manufacturing_object)
                    except Exception as e:
                        print('manufacturing_object error', e)

                    i = 0
                    for image in images:
                        AdminCommonMediaImagesFiles(request, image, 'Products', product_form.id)

                        i = i + 1

                    z = 0
                    print('Varient')
                    for variant_image in variant_images:
                        print('Varient3')
                        title = f'{product_form.code}-{variant_color[z]}-{variant_size[z]}'
                        variant_form = ProductVariants(product=product_form, title=title,
                                                       color=Variants.objects.get(title=variant_color[z],
                                                                                  option_type='Color'),
                                                       size=Variants.objects.get(title=variant_size[z],
                                                                                 option_type='Size'),
                                                       purchase_Variant=purchase_Variant[z],
                                                       sale_Variant=sale_Variant[z],
                                                       quantity=variant_quantity[z], image=variant_image)
                        if sale_Variant[z] == '':
                            pass
                        else:
                            variant_form.save()
                        z = z + 1

                    messages.success(request, _("Product Add Successfully"), extra_tags='Product')

                    return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogProductList'))

            else:

                messages.error(request, _("Product Not Add , Please Try Again"), extra_tags='Product')
        else:

            product_form = AdminCatalogProductForm()
            variant_form = AdminCatalogVariantsForm()
            translate_form = AdminCommonTranslateForm()
            context = {'manufacturer': manufacturer, 'warehouses': warehouses, 'product_form': product_form,

                       'relates': relates, 'variants': variants, 'attributes_group': attributes_group,
                       'variant_form': variant_form,
                       'translate_form': translate_form,

                       'current_page': _('Add'),
                       'prev_Page': _('Products'),
                       'prev_Page_link': reverse_lazy('catalog:AdminCatalogVariantList'),
                       }

            return render(request, f'{BACKEND_TEMPLATES}/catalog/product/add.html',
                          context=context
                          )
    except ObjectDoesNotExist:
        messages.error(request, _("You Are Not Vendor , Please Try Again"), extra_tags='Product')
        return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogProductList'))
    product_form = AdminCatalogProductForm()
    variant_form = AdminCatalogVariantsForm()
    translate_form = AdminCommonTranslateForm()

    context = {'manufacturer': manufacturer, 'warehouses': warehouses, 'product_form': product_form,

               'relates': relates, 'variants': variants, 'attributes_group': attributes_group,
               'variant_form': variant_form,
               'translate_form': translate_form,

               'current_page': _('Add'),
               'prev_Page': _('Products'),
               'prev_Page_link': reverse_lazy('catalog:AdminCatalogVariantList'),
               }

    return render(request, f'{BACKEND_TEMPLATES}/catalog/product/add.html',
                  context=context
                  )


@authenticated_staf
@staff_only
def AdminCatalogProductSimpleCreate(request):

    manufacturer = Manufacturer.objects.all()
    warehouses = Warehouse.objects.all()

    if request.method == "POST":
        product_form = AdminCatalogProductForm(request.POST or None, request.FILES or None)

        if product_form:
            category = request.POST.get('category')
            manufacturer_id = request.POST.get('manufacturer')
            title = request.POST.get('title')
            sku = request.POST.get('sku')
            unit = request.POST.get('unit')
            clinic_show = request.POST.get('clinic_show')
            for_sale = request.POST.get('for_sale')
            product_type = request.POST.get('product_type')
            can_return = request.POST.get('can_return')
            quantity = request.POST.get('quantity')
            minimum_quantity = request.POST.get('minimum_quantity')
            order_date = request.POST.get('order_date')
            expiration_date = request.POST.get('expiration_date')
            purchase_price = request.POST.get('purchase_price')
            sale_price = request.POST.get('sale_price')
            discount_active = request.POST.get('discount_active')
            discount_price = request.POST.get('discount_price')

            print(request.POST)
            try:
                category = Categories.objects.get(id=category)
            except:
                category = None
            try:
                manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            except:
                manufacturer = None
            if discount_active == 'Active':
                final_price = discount_price
            else:
                final_price = sale_price
            sku_check = Products.objects.filter(sku=sku).exists()
            if sku_check:
                messages.error(request, _("SKU Already Exist , Please Try Again"), extra_tags='Product')
                return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogProductSimpleCreate'))
            else:

                product_object = Products(sender_model=ContentType.objects.get(model='User'),
                                          sender_id=request.user.id,
                                          receiver_model=ContentType.objects.get(model='Warehouse'),
                                          receiver_id=thirdparty_warehouse.id,
                                          owner_model=ContentType.objects.get(model='Warehouse'),
                                          owner_id=thirdparty_warehouse.id,
                                          category=category, title=title,
                                          type=product_type, can_return=can_return,
                                          sku=sku, unit=unit, clinic_show=clinic_show, for_sale=for_sale,
                                          purchase_price=purchase_price, sale_price=sale_price,
                                          discount_active=discount_active, discount_price=discount_price,
                                          final_price=final_price, quantity=quantity,
                                          minimum_quantity=minimum_quantity, order_date=order_date,
                                          expiration_date=expiration_date,
                                          manufacturer=manufacturer, status='Active',
                                          )

                product_object.save()
                print('clinic_show', clinic_show)


                stock_object = ProductsStock(sender_model=ContentType.objects.get(model='User'),
                                             sender_id=request.user.id,
                                             receiver_model=ContentType.objects.get(model='Warehouse'),
                                             receiver_id=thirdparty_warehouse.id,
                                             owner_model=ContentType.objects.get(model='Products'),
                                             owner_id=product_object.id,
                                             title=title,
                                             type=product_type, can_return=can_return,
                                             sku=sku, unit=unit, for_sale=for_sale,
                                             purchase_price=purchase_price, sale_price=sale_price,
                                             discount_active=discount_active, discount_price=discount_price,
                                             final_price=final_price, quantity=quantity, stock=quantity,
                                             order_date=order_date,
                                             expiration_date=expiration_date,
                                             manufacturer=manufacturer, status='Active',
                                             )

                stock_object.save()
                messages.success(request, _("Product Add Successfully"), extra_tags='Product')
                return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogProductList'))
        else:
            messages.error(request, _("Product Not Add , Please Try Again"), extra_tags='Product')
    else:

        product_form = AdminCatalogProductForm()
        variant_form = AdminCatalogVariantsForm()
        translate_form = AdminCommonTranslateForm()
        context = {
            'manufacturer': manufacturer,
            'warehouses': warehouses,
            'product_form': product_form,
            'current_page': _('Add'),
            'prev_Page': _('Products'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogProductList'),
        }

        return render(request, f'{BACKEND_TEMPLATES}/catalog/product/miniadd.html',
                      context=context
                      )

    product_form = AdminCatalogProductForm()

    context = {
        'manufacturer': manufacturer,
        'warehouses': warehouses,
        'product_form': product_form,
        'current_page': _('Add'),
        'prev_Page': _('Products'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogProductList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/catalog/product/miniadd.html',
                  context=context
                  )


@authenticated_staf
@staff_only
def AdminDetailsCatalogProduct(request, slug):
    context = {

    }

    return render(request, f'{BACKEND_TEMPLATES}/catalog/product/add.html', context)


@authenticated_staf
@staff_only
def AdminCatalogProductUpdate(request, slug):
    check_user = User.objects.get(id=request.user.id)
    if check_user.access_level == 'ThirdPartyService' or check_user.access_level == 'Employee':
        if check_user.access_level == 'ThirdPartyService':
            warehouse_check = Warehouse.objects.get_or_create(sender_model=ContentType.objects.get(model='User'),
                                                              sender_id=request.user.id,
                                                              owner_model=ContentType.objects.get(model='User'),
                                                              owner_id=request.user.id,
                                                              name='Main Warehouse')
            thirdparty_warehouse = Warehouse.objects.get(owner_id=check_user.id)
            product = Products.objects.get(slug=slug)



        elif check_user.access_level == 'Employee':
            thirdparty_warehouse = Warehouse.objects.get(receiver_id=check_user.id)
            product = Products.objects.get(slug=slug)
        else:
            thirdparty_warehouse = None
            messages.error(request, _("You Don't Have Permission To Access This Page ,Or You dont Have Facility Yet"),
                           extra_tags='Product')
            context = {
                'check_user': check_user,
                'thirdparty_warehouse': thirdparty_warehouse,

                'current_page': _('Products'),
            }
            return render(request, f'{BACKEND_TEMPLATES}/thirdparty/services/admin.html', context)

    else:
        messages.error(request, _("You Don't Have Permission To Access This Page"), extra_tags='General')
        return HttpResponseRedirect(reverse_lazy('core:AdminError404'))
    manufacturer = Manufacturer.objects.all()
    warehouses = Warehouse.objects.all()
    if request.method == "POST":
        product_form = AdminCatalogProductForm(request.POST or None, request.FILES or None)
        if product_form:
            category = request.POST.get('category')
            manufacturer_id = request.POST.get('manufacturer')
            title = request.POST.get('title')
            sku = request.POST.get('sku')
            unit = request.POST.get('unit')
            clinic_show = request.POST.get('clinic_show')
            for_sale = request.POST.get('for_sale')
            product_type = request.POST.get('product_type')
            can_return = request.POST.get('can_return')
            minimum_quantity = request.POST.get('minimum_quantity')
            discount_active = request.POST.get('discount_active')
            discount_price = request.POST.get('discount_price')
            try:
                category = Categories.objects.get(id=category)
            except:
                category = None
            try:
                manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            except:
                manufacturer = None
            sku_check = Products.objects.filter(sku=sku).exclude(slug=slug).exists()
            if sku_check:
                messages.error(request, _("SKU Already Exist , Please Try Again"), extra_tags='Product')
                return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogProductUpdate', kwargs={'slug': slug}))
            else:
                product_object = Products.objects.get(slug=slug)
                product_object.category = category
                product_object.manufacturer = manufacturer
                product_object.title = title
                product_object.type = product_type
                product_object.can_return = can_return
                product_object.sku = sku
                product_object.unit = unit
                product_object.clinic_show = clinic_show
                product_object.for_sale = for_sale
                product_object.minimum_quantity = minimum_quantity
                product_object.discount_active = discount_active
                product_object.discount_price = discount_price
                product_object.save()
                print('clinic_show', clinic_show)




                messages.success(request, _("Product Add Successfully"), extra_tags='Product')
                return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogProductList'))
        else:
            messages.error(request, _("Product Not Add , Please Try Again"), extra_tags='Product')
    else:

        product_form = AdminCatalogProductForm()
        variant_form = AdminCatalogVariantsForm()
        translate_form = AdminCommonTranslateForm()
        context = {
            'manufacturer': manufacturer,
            'warehouses': warehouses,
            'product': product,
            'product_form': product_form,
            'current_page': _('Update'),
            'prev_Page': _('Products'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogProductList'),
        }

        return render(request, f'{BACKEND_TEMPLATES}/catalog/product/miniupdate.html',
                      context=context
                      )

    product_form = AdminCatalogProductForm()

    context = {
        'manufacturer': manufacturer,
        'warehouses': warehouses,
        'product': product,
        'product_form': product_form,
        'current_page': _('Update'),
        'prev_Page': _('Products'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogProductList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/catalog/product/miniupdate.html',
                  context=context
                  )


@authenticated_staf
@staff_only
def AdminDeleteCatalogProduct(request, slug):
    context = {

    }

    return render(request, f'{BACKEND_TEMPLATES}/catalog/product/add.html', context)


def AdminProductFinalPrice(request):
    data = {}
    vendor = Vendor.objects.get(vendor=request.user.id)
    category = Categories.objects.get(title=vendor.category)
    sale_price = request.GET.get('sale_price')
    discount_price = request.GET.get('discount_price')
    discount_active = request.GET.get('discount_active')
    commission = CommissionCategory.objects.get(category=category).commission

    if discount_active == 'Yes':
        print(Decimal(discount_price))
        print(Decimal(commission))
        commission = (Decimal(discount_price) * Decimal(commission)) / 100
        final_price = commission + Decimal(discount_price)
        print(final_price)
        context = {
            'final_price': final_price,

        }
        data = {'rendered_table': render_to_string('vendor/catalog/product/final_price.html', context=context)}
        return JsonResponse(data, status=200)
    elif discount_active in ['NO', '']:
        commission = (Decimal(sale_price) * Decimal(commission)) / 100
        final_price = commission + Decimal(sale_price)
        print(final_price)
        context = {
            'final_price': final_price,

        }
        data = {'rendered_table': render_to_string('vendor/catalog/product/final_price.html', context=context)}
        return JsonResponse(data, status=200)
    else:
        messages.error(request, "Error")

    data = {'rendered_table': render_to_string('vendor/catalog/product/final_price.html')}

    return JsonResponse(data, status=200)


def AdminProductManufacturingCalculate(request, product, ):
    try:
        product = Products.objects.get(id=product)
        manufacturing_object = ProductManufacturing.objects.filter(product=product)
        for manufacturing in manufacturing_object:
            ore = manufacturing.ore
            ore_get = Products.objects.get(id=ore.id)
            ore_get.quantity = ore_get.quantity - manufacturing.quantity
            ore_get.save()
    except ObjectDoesNotExist:
        messages.error(request, _("Product Not Add , Please Try Again"), extra_tags='Product')


########################## Variants ######################
@authenticated_staf
@staff_only
def AdminCatalogVariantsList(request):
    variants = Variants.objects.all()

    if request.method == "POST":
        variant_form = AdminCatalogVariantsForm(request.POST or None, request.FILES or None)

        if variant_form.is_valid():
            title = request.POST.get('title')
            option_type = request.POST.get('option_type')
            code = request.POST.get('code')
            divided = request.POST.get('divided')


            variant_object = Variants(title=title, option_type=option_type, code=code, divided=divided,)

            variant_object.save()


            messages.success(request, _("Variants Add Successfully"), extra_tags='Variants')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogVariantList'))
        else:

            messages.error(request, _("Variants Not Add , Please Try Again"), extra_tags='Variants')
    else:
        context = {
            'variants': variants,

            'variant_form': AdminCatalogVariantsForm(),

            'current_page': _('Variant')

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/variant/admin.html', context)
    context = {
        'variants': variants,

        'variant_form': AdminCatalogVariantsForm(),

        'current_page': _('Unit')

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/variant/admin.html', context)


@authenticated_staf
@staff_only
def AdminCatalogVariantsUpdate(request, slug):
    variant = Variants.objects.get(slug=slug)


    if request.method == "POST":
        variant_form = AdminCatalogVariantsForm(request.POST or None, request.FILES or None)

        if variant_form:

            title = request.POST.get('title')
            option_type = request.POST.get('option_type')
            code = request.POST.get('code')
            divided = request.POST.get('divided')


            variant_object = Variants.objects.get(slug=slug)
            variant_object.title = title
            variant_object.option_type = option_type
            variant_object.code = code
            variant_object.divided = divided
            variant_object.save()

            messages.success(request, _("Variants Add Successfully"), extra_tags='Variants')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogVariantList'))
        else:

            messages.error(request, _("Variants Not Add , Please Try Again"), extra_tags='Variants')
    else:
        context = {
            'variant': variant,

            'variant_form': AdminCatalogVariantsForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Update'),
            'prev_Page': _('variants'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogVariantList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/variant/update.html', context)

    context = {
        'variant': variant,

        'variant_form': AdminCatalogVariantsForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Update'),
        'prev_Page': _('variants'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogVariantList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/variant/update.html', context)


class AdminCatalogVariantsDelete(DeleteView):
    model = Variants
    fields = '__all__'
    success_url = reverse_lazy('core:AdminCatalogVariantList')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(AdminCatalogVariantsDelete, self).dispatch(*args, **kwargs)

########################## units ######################



@authenticated_staf
@staff_only
def AdminCatalogUnitsList(request):
    units = UnitConversion.objects.all()

    if request.method == "POST":
        unit_form = AdminCatalogUnitConversionForm(request.POST or None, request.FILES or None)

        if unit_form.is_valid():
            title = request.POST.get('title')
            unit_base = request.POST.get('unit_base')
            unit = request.POST.get('unit')
            unit_base_value = request.POST.get('unit_base_value')
            unit_value = request.POST.get('unit_value')
            if unit_base == unit:
                messages.error(request, _("Unit Base and Unit can't be same"), extra_tags='Unit')
                return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogUnitsList'))
            unit_object = UnitConversion(title=title,unit_base=unit_base,unit=unit,  unit_base_value=unit_base_value, unit_value=unit_value,status='Active')
            unit_object.save()
            messages.success(request, _("Unit Add Successfully"), extra_tags='Unit')
            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogUnitsList'))
        else:
            messages.error(request, _("Unit Not Add , Please Try Again"), extra_tags='Unit')
    else:
        context = {
            'units': units,
            'unit_form': AdminCatalogUnitConversionForm(),
            'current_page': _('Unit')

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/unit/admin.html', context)


@authenticated_staf
@staff_only
def AdminCatalogUnitsUpdate(request, slug):
    unit = UnitConversion.objects.get(slug=slug)

    if request.method == "POST":
        unit_form = AdminCatalogUnitConversionForm(request.POST or None, request.FILES or None)

        if unit_form.is_valid():
            title = request.POST.get('title')
            unit_base = request.POST.get('unit_base')
            unit = request.POST.get('unit')

            unit_base_value = request.POST.get('unit_base_value')
            unit_value = request.POST.get('unit_value')
            if unit_base == unit:
                messages.error(request, _("Unit Base and Unit can't be same"), extra_tags='Unit')
                return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogUnitsUpdate' , kwargs={'slug':slug} ))
            unit_object = UnitConversion.objects.get(slug=slug)
            unit_object.title = title
            unit_object.unit_base = unit_base
            unit_object.unit = unit
            unit_object.unit_base_value = unit_base_value
            unit_object.unit_value = unit_value
            unit_object.save()
            messages.success(request, _("Unit Add Successfully"), extra_tags='Unit')
            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogUnitsList'))
        else:
            messages.error(request, _("Unit Not Add , Please Try Again"), extra_tags='Unit')
    else:
        context = {
            'unit': unit,
            'unit_form': AdminCatalogUnitConversionForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Update'),
            'prev_Page': _('Unit'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogUnitsList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/unit/update.html', context)

    context = {
        'unit': unit,
        'unit_form': AdminCatalogUnitConversionForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Update'),
        'prev_Page': _('Unit'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogUnitList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/unit/update.html', context)

@authenticated_staf
@staff_only
def AdminCatalogUnitsDelete(request, slug):
    unit = UnitConversion.objects.get(slug=slug)
    unit.delete()
    messages.success(request, _("Unit Delete Successfully"), extra_tags='Unit')
    return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogUnitList'))

########################## Manufacturer ######################
@authenticated_staf
@staff_only
def AdminCatalogManufacturerList(request):
    manufacturers = Manufacturer.objects.all()
    manufacturer_list = []
    for manufacturer in manufacturers:
        translate = CommonTranslate.objects.get(
            owner_model=ContentType.objects.get(model='Manufacturer'), owner_id=manufacturer.id)

        manufacturer_list.append(
            {"manufacturer": manufacturer, "translate": translate, })

    if request.method == "POST":
        manufacturer_form = AdminCatalogManufacturerForm(request.POST or None, request.FILES or None)
        if manufacturer_form:
            title = request.POST.get('title')
            title_tr = request.POST.get('title_tr')
            manufacturer_form = Manufacturer(title=title, status='Active')
            manufacturer_form.save()
            translate = CommonTranslate(title=title,
                                        owner_model=ContentType.objects.get(model='Manufacturer'),
                                        owner_id=manufacturer_form.id)
            translate.save()

            messages.success(request, _("Manufacturer Add Successfully"), extra_tags='Manufacturer')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogManufacturerList'))
        else:

            messages.error(request, _("Manufacturer Not Add , Please Try Again"), extra_tags='Manufacturer')
    else:
        context = {
            'manufacturers': manufacturer_list,

            'manufacturer_form': AdminCatalogManufacturerForm(),

            'current_page': _('Manufacturer')

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/manufacturer/admin.html', context)
    context = {
        'manufacturers': manufacturer_list,

        'manufacturer_form': AdminCatalogManufacturerForm(),

        'current_page': _('Manufacturer')

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/manufacturer/admin.html', context)


@authenticated_staf
@staff_only
def AdminCatalogManufacturerUpdate(request, slug):
    manufacturer = Manufacturer.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='Manufacturer'), owner_id=manufacturer.id)

    if request.method == "POST":
        manufacturer_form = AdminCatalogManufacturerForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if manufacturer_form.is_valid() and translate_form.is_valid():

            title = request.POST.get('title')
            image = request.FILES.get('image')
            status = request.POST.get('status')
            title_tr = request.POST.get('title_tr')

            manufacturer_object = Manufacturer.objects.get(slug=slug)
            manufacturer_object.title = title
            manufacturer_object.image = image
            manufacturer_object.status = status

            manufacturer_object.save()
            translate = CommonTranslate.objects.get(
                owner_model=ContentType.objects.get(model='Manufacturer'),
                owner_id=manufacturer_object.id)
            translate.title = title_tr

            translate.save()
            messages.success(request, _("Manufacturer Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogManufacturerList'))
        else:

            messages.error(request, _("Manufacturer Not Add , Please Try Again"), extra_tags='Category')
    else:
        context = {
            'manufacturer': manufacturer,
            'translate': translate,
            'manufacturer_form': AdminCatalogManufacturerForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Update'),
            'prev_Page': _('Manufacturer'),
            'prev_Page_link': reverse_lazy('catalog:AdminCatalogManufacturerList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/catalog/manufacturer/update.html', context)

    context = {
        'manufacturer': manufacturer,
        'translate': translate,
        'manufacturer_form': AdminCatalogManufacturerForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Update'),
        'prev_Page': _('Manufacturer'),
        'prev_Page_link': reverse_lazy('catalog:AdminCatalogManufacturerList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/catalog/manufacturer/update.html', context)


class AdminCatalogManufacturerDelete(DeleteView):
    model = Manufacturer
    fields = '__all__'
    success_url = reverse_lazy('core:AdminCatalogManufacturerList')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(AdminCatalogManufacturerDelete, self).dispatch(*args, **kwargs)
