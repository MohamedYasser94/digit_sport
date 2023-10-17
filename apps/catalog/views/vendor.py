from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView, View

from core.forms.core import AdminCommonProfileForm, AdminCommonMediaFilesForm, AdminCommonSocialLinkForm
from core.forms.vendor import AdminCreateVendorForm
from core.models.localization import Country, City, Governorates, Area
from core.models.vendor import Vendor
from core.utils.notification import create_notification_admin, notify_admin, notify_vendor
from core.views.people import AdminClientCommonCreate
from core.views.core import AdminCommonMediaHeroFiles, AdminCommonTranslate, AdminCommonProfile, AdminCommonSocialLink
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import vendor_only, authenticated_user

User = get_user_model()



@authenticated_user
def AdminVendorRegister(request, nuc):
    current_user = User.objects.get(nuc=nuc)

    if request.method == 'POST':
        vendor_form = AdminCreateVendorForm(request.POST, request.FILES, )
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        if vendor_form.is_valid() and profile_form and media_form and social_form:
            title = vendor_form.cleaned_data["title"]
            email = vendor_form.cleaned_data["email"]
            category = vendor_form.cleaned_data["category"]
            company = request.POST.get('company')
            national_id = request.POST.get('national_id')
            hero_image = request.POST.get('hero_image')
            phone = request.POST.get('phone')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            title_tr = request.POST.get('title_tr')
            city = request.POST.get('city')
            area = request.POST.get('area')
            address = request.POST.get('address')
            provider = request.POST.getlist('provider')
            urls = request.POST.getlist('urls')
            vendor_id = current_user.id
            try:
                country = Country.objects.get(id=country)
            except Exception as e:
                country = None
            try:
                governorates = Governorates.objects.get(id=governorates)
            except Exception as e:
                governorates = None
            try:
                city = City.objects.get(id=city)
            except Exception as e:
                city = None
            try:
                area = Area.objects.get(id=area)
            except Exception as e:
                area = None


            vendor = User.objects.filter(seller=True)
            status = Vendor.objects.filter(status=False, vendor_id=vendor_id)

            title_exists = Vendor.objects.filter(title=title).exists()
            if vendor and status:
                messages.error(request,
                               format_html('''You already have a vendor wait for activate &nbsp; &nbsp;  or learn how to sell &nbsp; 
                                    <a href=""> Edit</a> ''', reverse('home:HomeIndex', )))
                return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create.html', )
            elif title_exists:
                messages.error(request,
                               format_html('''This Store Name Already Taken wait for activate &nbsp; &nbsp;  or learn how to sell &nbsp; 
                                                        <a href=""> Edit</a> ''', reverse('home:HomeIndex', )))

                return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create.html', )
            else:
               
              
                vendor_form = Vendor(title=title, email=email,  vendor_id=vendor_id, category=category)
                vendor_form.save()
                new_vendor = User.objects.get(nuc=nuc,id=vendor_id)
                new_vendor.seller=True
                new_vendor.save()
                AdminCommonTranslate(request, title_tr, None, None, 'Vendor', vendor_form.id)
                AdminClientCommonCreate(request, title, company, national_id, email, 'Vendor', 'Active',
                                        phone, 'Business', address, country, governorates, city, area, None,hero_image)
                AdminCommonMediaHeroFiles(request, hero_image, 'Vendor', vendor_form.id)
                AdminCommonProfile(request, phone, 'Business', address, country, governorates, city, area, None,
                                   'Vendor', vendor_form.id)

                try:
                    a = 0
                    for url in urls:
                        if  url != '':
                            AdminCommonSocialLink(request, provider[a], url, 'Vendor', vendor_form.id)
                        a = a + 1
                except Exception as e:
                    pass
                   

                try:
                    admins = User.objects.filter(is_superuser=True)
                    for admin in admins:
                        create_notification_admin(request, admin, 'NewVendorRegistration', extra_id=vendor_form.id, extra_slug=vendor_form.slug,
                                                  extra_info=vendor_form.title,more_info=vendor_form.vendor, extra_time=vendor_form.create_at,
                                                  extra_notify=vendor_form.create_at)

                    notify_admin(vendor_form)

                    notify_vendor(vendor_form,'Your Store Wanting For Confirm','Thanks To Use Our Site')
                except Exception as e:
                    messages.error(request, _(f"Store Not Add ,{e}: Please Try Again"), extra_tags='Store')
                    vendor_form = AdminCreateVendorForm()
                    context = {
                        'current_user': current_user,
                        'vendor_form': vendor_form,
                        'profile_form': AdminCommonProfileForm(),
                        'media_form': AdminCommonMediaFilesForm(),
                        'social_form': AdminCommonSocialLinkForm(),
                        'current_page': _('Clients')
                    }
                    return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create.html', context)

                # return HttpResponse("OK")
                messages.success(request, _("Store Add Successfully"), extra_tags='Store')
                return HttpResponseRedirect(reverse_lazy('core:AdminVendorCreateSuccess'))
        else:
          
           
            messages.error(request, _("Store Not Add , Please Try Again"), extra_tags='Store')
            context = {
                'current_user': current_user,
                'vendor_form': vendor_form,
                'profile_form': AdminCommonProfileForm(),
                'media_form': AdminCommonMediaFilesForm(),
                'social_form': AdminCommonSocialLinkForm(),
                'current_page': _('Clients')
            }
            return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create.html', context)
    else:
        vendor_form = AdminCreateVendorForm()
        context = {
            'current_user': current_user,
            'vendor_form': vendor_form,
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'social_form': AdminCommonSocialLinkForm(),
            'current_page': _('Clients')
        }
        return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create.html', context)

@login_required(login_url='/login')
def CreateSuccess(request, ):
    is_seller = User.objects.filter(id=request.user.id, seller=True)
    if request.user.is_authenticated and is_seller:
        vendor = Vendor.objects.get(vendor_id=request.user.id).code
        context = {
            'vendor': vendor
        }
        return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create-success.html', context)
    else:
        return render(request, f'{BACKEND_TEMPLATES}/vendor/dashboard/create-success.html')
#
# @login_required(login_url='/login')  # Check login
# def AlreadyUserSellerRegister(request, slug):
#     user = User.objects.get(id=request.user.id)
#     forms = AlreadyUserSellerRegisterForm(instance=user)
#
#     if request.method == 'POST':
#         forms = AlreadyUserSellerRegisterForm(request.POST, request.FILES, instance=user)
#         if forms.is_valid():
#
#             seller = forms.cleaned_data['seller']
#             forms = User.objects.get(id=request.user.id)
#             forms.seller = seller
#
#             forms.save()
#             return redirect('home:index', )
#         else:
#           
#            
#             context = {
#                 'user': user,
#                 'forms': forms
#             }
#             messages.error(request, "Error")
#             return render(request, f'{FRONTEND_TEMPLATES}/login/CustomerLogin.html', context)
#
#     else:
#         context = {
#             'user': user,
#             'forms': forms
#         }
#         return render(request, 'accounts/AlreadyUserSellerRegister.html', context)
#
#
# # ADD AuthenticationForm
# class VendorCreate(View):
#     def get(self, request, *args, **kwargs):
#         form = AdminCreateVendorForm()
#         context = {
#             'form': form,
#         }
#         return render(request, "store-page/create-store.html", context)
#
#     def post(self, request, *args, **kwargs):
#         if request.method == 'POST':
#
#             form = AdminCreateVendorForm(request.POST, request.FILES, )
#
#             if form.is_valid():
#                 title = form.cleaned_data["title"]
#                 email = form.cleaned_data["email"]
#                 phone = form.cleaned_data["phone"]
#                 company = form.cleaned_data["company"]
#                 category = form.cleaned_data["category"]
#                 country = form.cleaned_data["country"]
#                 governorates = form.cleaned_data["governorates"]
#                 city = form.cleaned_data["city"]
#                 code = get_random_string(25).upper()  # random cod
#                 vendor_id = request.user.id
#                
#                 vendor = User.objects.filter(seller=True)
#                 status = Vendor.objects.filter(status=False, vendor_id=vendor_id)
#
#                 title_exists = Vendor.objects.filter(title=title).exists()
#                 if vendor and status:
#                     messages.error(request,
#                                    format_html('''You already have a vendor wait for activate &nbsp; &nbsp;  or learn how to sell &nbsp;
#                                         <a href=""> Edit</a> ''', reverse('home:index', )))
#                     return render(request, "store-page/create-store.html", )
#                 elif title_exists:
#                     messages.error(request,
#                                    format_html('''This Store Name Already Taken wait for activate &nbsp; &nbsp;  or learn how to sell &nbsp;
#                                                             <a href=""> Edit</a> ''', reverse('home:index', )))
#
#                     return render(request, "store-page/create-store.html", )
#                 else:
#                     form = Vendor(title=title, phone=phone, email=email, company=company, country=country,
#                                   governorates=governorates, city=city, vendor_id=vendor_id, code=code,
#                                   category=category)
#                     form.save()
#                     admin = User.objects.filter(admin=True)
#                     print(admin)
#                     try:
#                         create_notification_admin(request, admin, 'NewVendorCreate', extra_id=form.id,
#                                                   extra_info=vendor_id)
#                         notify_admin(form)
#                         # notify_user(form)
#                     except Exception as e:
#                         messages.error(request, e)
#                         form = AdminCreateVendorForm()
#                         context = {
#                             'form': form,
#                         }
#                         return render(request, "store-page/create-store.html", context)
#
#                     # return HttpResponse("OK")
#                     return HttpResponseRedirect(reverse_lazy('vendors:CreateSuccess'))
#             else:
#               
#                
#                 messages.error(request, "Error")
#                 context = {
#                     'form': form,
#                 }
#                 return render(request, "store-page/create-store.html", context)
#         else:
#             form = AdminCreateVendorForm()
#             context = {
#                 'form': form,
#             }
#             return render(request, "store-page/create-store.html", context)
#
#
#
#
#
# @login_required(login_url='/login')
# def StoreWaiting(request):
#     if not request.user.is_authenticated:
#         return render(request, 'front/ErrorPage/404.html')
#     status = Vendor.objects.filter(status=False)
#     context = {'status': status,
#                }
#     return render(request, 'store-page/store-waiting.html', context)
#
#
# # def AllVendor(request):
# #     if not request.user.is_authenticated:
# #         return HttpResponseRedirect(reverse('user:CustomerLogin'))
# #     else:
# #         return render(request, "all-vendor/all-vendor.html",
# #                      )
#
#
# class VendorLoginView(View):
#     """
#     Description:Will be used to login and logout users.\n
#     """
#     template_name = 'vendor/vendor-base/VendorLogin.html'
#
#     def get(self, request, *args, **kwargs):
#
#         if request.user.is_authenticated:
#             return redirect('vendors:VendorIndex')
#         else:
#             login_form = UserLoginForm()
#             signup_form = SellerRegisterForm()
#             context = {
#                 "title": "Login",
#                 "login_form": login_form,
#                 "signup_form": signup_form,
#             }
#             return render(request, self.template_name, context)
#
#     def post(self, request, *args, **kwargs):
#         login_form = UserLoginForm(request.POST or None)
#
#         next_ = request.GET.get('next')
#         next_post = request.POST.get('next')
#         redirect_path = next_ or next_post or None
#
#         if login_form.is_valid():
#             email = login_form.cleaned_data.get("email")
#             password = login_form.cleaned_data.get("password")
#             user = authenticate(email=email, password=password)
#
#             if user is not None:
#                 login(request, user)
#                 user_logged_in.send(
#                     user.__class__,
#                     instance=user,
#                     request=request
#                 )
#                 if not url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
#                     messages.error(request, "Error")
#                    
#                    
#             else:
#                 print("error")
#                 messages.error(request, "Error")
#             return HttpResponseRedirect(reverse_lazy('vendors:VendorLogin'))
#         context = {
#             "title": "Login",
#             "login_form": login_form
#         }
#         return render(request, self.template_name, context)
#
#
# def VendorLogout(request):
#     logout(request)
#     return redirect('vendors:VendorLogin')


class VendorDashboard(View):
    def get(self, request, *args, **kwargs, ):
        slug = kwargs["slug"]
        user = request.user.id
        try:
            if request.user.is_authenticated and Vendor.objects.get(slug=slug, vendor__id=user):
                store = []
                vendor = Vendor.objects.get(slug=slug, vendor__id=user)

                product = Products.objects.filter(seller__id=vendor.vendor.id)
                order = OrderProduct.objects.filter(vendor=vendor, status__in=[
                    OrderProduct.New,
                    OrderProduct.Accepted,
                    OrderProduct.Preparing,
                    OrderProduct.OnShipping,
                    OrderProduct.Canceled,
                    OrderProduct.Refund,
                ])
                sales = OrderProduct.objects.filter(vendor=vendor, status='Completed')
                pending = OrderProduct.objects.filter(vendor=vendor, status='Accepted')
                store.append({"vendor": vendor, "product": product,
                              "order": order, "sales": sales, "pending": pending})
                trending_product = SalesProductCount.objects.filter(vendor=vendor, order__status='Completed')
                settings = UserSetting.objects.get(user=user)
                context = {
                    "store": store,
                    "trending_product": trending_product,
                    "settings": settings,
                }

                return render(request, "vendor/vendor-base/vendor-dashboard.html",
                              context)
            else:
                return render(request, 'front/ErrorPage/403.html')
        except Exception as e:
           
            return render(request, 'front/ErrorPage/403.html')


class EditStore(View):
    def get(self, request, *args, **kwargs, ):
        slug = kwargs["slug"]
        print(slug)
        user = request.user.id
        form = VendorStoreEditForm()
        try:
            if Vendor.objects.get(slug=slug, vendor__id=user):
                vendor = Vendor.objects.get(slug=slug, vendor__id=user)

                return render(request, "vendor/vendor-base/vendor-edit-store-profile.html",
                              {"vendor": vendor, "form": form, })
            else:
                return render(request, 'front/ErrorPage/404.html')
        except Exception as e:
           
            return render(request, 'front/ErrorPage/refresh-page.html')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = VendorStoreEditForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                user = request.user.id
                title = request.POST.get("title")
                vendor = request.POST.get("vendor")
                phone = request.POST.get("phone")
                company = request.POST.get("company")
                image = form.cleaned_data['image']
                about = request.POST.get("about")
                keywords = request.POST.get("keywords")
                country = form.cleaned_data['country']
                governorates = form.cleaned_data['governorates']
                city = form.cleaned_data['city']
                area = form.cleaned_data['area']
                slug = request.POST.get("slug")
                address = request.POST.get("address")
                facebook = request.POST.get("facebook")
                instagram = request.POST.get("instagram")
                twitter = request.POST.get("twitter")
                youtube = request.POST.get("youtube")

                store = Vendor.objects.get(slug=slug)
                vendor = User.objects.get(id=user)
                store.vendor = vendor
                store.title = title
                store.phone = phone
                store.company = company
                store.image = image
                store.country = country
                store.governorates = governorates
                store.city = city
                store.area = area
                store.about = about
                store.keywords = keywords
                store.slug = slug
                store.address = address
                store.facebook = facebook
                store.instagram = instagram
                store.twitter = twitter
                store.youtube = youtube
                store.save()
               
               
            else:
                messages.error(request, "Error")
                user = request.user.id
                slug = kwargs["slug"]
                vendor = Vendor.objects.get(vendor_id=user)
                return render(request, "vendor/vendor-base/vendor-edit-store-profile.html",
                              {"vendor": vendor, "form": form, })
        else:
            form = VendorStoreEditForm()
            user = request.user.id
            slug = kwargs["slug"]
            vendor = Vendor.objects.get(vendor_id=user)
            return render(request, "vendor/vendor-base/vendor-edit-store-profile.html",
                          {"vendor": vendor, "form": form, })

        return redirect(reverse('vendors:VendorDashboard', kwargs={"slug": slug}, )
                        )

        # return HttpResponse("OK")

        # return HttpResponseRedirect(reverse_lazy('vendors:VendorDashboard' ))


class VendorEditStore(View):
    def get(self, request, *args, **kwargs, ):
        user = request.user.id
        form = VendorStoreEditForm()
        try:
            if Vendor.objects.get(vendor__id=user):
                vendor = Vendor.objects.get(vendor__id=user)

                return render(request, "vendor/settings/vendor-update-store.html",
                              {"vendor": vendor, "form": form, })
            else:
                return render(request, 'front/ErrorPage/404.html')
        except Exception as e:
           
            return render(request, 'front/ErrorPage/403.html')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = VendorStoreEditForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                user = request.user.id
                title = request.POST.get("title")
                user = request.POST.get("vendor")
                phone = request.POST.get("phone")
                company = request.POST.get("company")
                image = form.cleaned_data['image']
                about = request.POST.get("about")
                keywords = request.POST.get("keywords")
                country = form.cleaned_data['country']
                governorates = form.cleaned_data['governorates']
                city = form.cleaned_data['city']
                area = form.cleaned_data['area']
                slug = request.POST.get("slug")
                address = request.POST.get("address")
                facebook = request.POST.get("facebook")
                instagram = request.POST.get("instagram")
                twitter = request.POST.get("twitter")
                youtube = request.POST.get("youtube")

                store = Vendor.objects.get(vendor_id=user)
                vendor = User.objects.get(id=user)
                store.vendor = vendor
                store.title = title
                store.phone = phone
                store.company = company
                store.image = image
                store.country = country
                store.governorates = governorates
                store.city = city
                store.area = area
                store.about = about
                store.keywords = keywords
                store.slug = slug
                store.address = address
                store.facebook = facebook
                store.instagram = instagram
                store.twitter = twitter
                store.youtube = youtube
                store.save()
               
               
            else:
                messages.error(request, "Error")
                user = request.user.id
                slug = kwargs["slug"]
                vendor = Vendor.objects.get(vendor_id=user)
                return render(request, "vendor/settings/vendor-update-store.html",
                              {"vendor": vendor, "form": form, })
        else:
            form = VendorStoreEditForm()
            user = request.user.id

            vendor = Vendor.objects.get(vendor_id=user)
            return render(request, "vendor/settings/vendor-update-store.html",
                          {"vendor": vendor, "form": form, })
        messages.success(request, "Info Update")
        return HttpResponseRedirect(reverse_lazy('vendors:VendorIndex'))


@login_required(login_url='/vendor')
@vendor_only
def store_delete(request, user_id):
    store = Vendor.objects.get(id=user_id)
    store.is_delete = True
    store.save()
    return redirect('vendors')


# Seller catalog list and details


class SellerProductDetailRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Products, pk=kwargs['pk'])
        return obj.get_absolute_url()


# Seller transaction lists
'''''
class SellerTransactionListView(SellerAccountMixin, ListView):
	model = Transaction
	template_name = "sellers/transaction_list_view.html"

	def get_queryset(self):
		return self.get_transactions()



# Seller dashboard-bases

class SellerDashboard(SellerAccountMixin, FormMixin, View):
    form_class = NewSellerForm
    success_url = "/seller/"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        apply_form = self.get_form()  # NewSellerForm()
        users = self.get_account()
        exists = users
        active = None
        context = {}
        if exists:
            active = users.active
        if not exists and not active:
            context["title"] = "Apply for Account"
            context["apply_form"] = apply_form
        elif exists and not active:
            context["title"] = "Account Pending"
        elif exists and active:
            context["title"] = "Seller Dashboard"
            context["products"] = self.get_products()
            transactions_today = self.get_transactions_today()
            context["transactions_today"] = transactions_today
            context["today_sales"] = self.get_today_sales()
            context["total_sales"] = self.get_total_sales()
            context["transactions"] = self.get_transactions().exclude(pk__in=transactions_today)[:5]
        else:
            pass

        return render(request, "sellers/dashboard-bases.html", context)

    def form_valid(self, form):
        valid_data = super(SellerDashboard, self).form_valid(form)
        obj = SellerAccount.objects.create(user=self.request.user)
        return valid_data
'''
