from django.contrib import messages
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from fcm_django.models import FCMDevice

from core.models.notifications import DeviceInfo
from core.utils.notification import notify_user
from digit_sport import settings
from core.forms.users import AdminUserSignUpForm, UserUpdateForm, AdminGroupForm, UserProfileForm, \
    AdminUserLoginForm, AdminUserUpdateForm, UserProfileUpdateForm
from core.models.localization import Country, Language
from core.models.services import Newsletter, Contact
from core.models.social import FriendList, FriendRequest
from core.utils.friend_request_status import FriendRequestStatus, get_friend_request_or_false
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, unauthenticated_user, authenticated_user, staff_only, authenticated_staf, \
    admin_only
from user.models import UserGeoInfo, UserProfile
from user.signals import user_logged_in

User = get_user_model()


class AdminLogin(View):
    """
    Description:Will be used to log in and logout users.\n
    """
    template_name = f'backend/{BACKEND_TEMPLATES}/login.html'

    def get(self, request, *args, **kwargs):
        form = AdminUserLoginForm()
        context = {
            "title": "Login",
            "form": form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = AdminUserLoginForm(request.POST or None)

        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data['remember_me']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(
                        0)  # <-- Here if they remember me is False, that is why expiry is set to 0 seconds. So it will automatically close the session after the browser is closed.

            if user is not None:
                login(request, user)
                user_logged_in.send(
                    user.__class__,
                    instance=user,
                    request=request
                )

                return redirect("/dashboard/")

            else:
                print("error")
                return redirect("/dashboard/")

        context = {
            "title": "Login",
            "form": form
        }
        return render(request, self.template_name, context)

    @method_decorator(unauthenticated_user, csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AdminLogin, self).dispatch(*args, **kwargs)


class AdminLockscreen(View):
    """
    Description:Will be used to login and logout users.\n
    """
    template_name = 'users/lockscreen.html'

    def get(self, request, *args, **kwargs):
        del request.session['email']
        form = AdminUserLoginForm()
        context = {
            "title": "Login",
            "form": form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = AdminUserLoginForm(request.POST or None)

        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)

            if user is not None:
                login(request, user)
                user_logged_in.send(
                    user.__class__,
                    instance=user,
                    request=request
                )
                return redirect("/dashboard/")

            else:
                print("error")
                return redirect("/dashboard/login/")

        context = {
            "title": "Login",
            "form": form
        }
        return render(request, self.template_name, context)

    @method_decorator(authenticated_user)
    def dispatch(self, *args, **kwargs):
        return super(AdminLockscreen, self).dispatch(*args, **kwargs)


@login_required(login_url='/login')
def AdminLogout(request):
    logout(request)
    messages.success(request, "Logout Successfully!")
    return HttpResponseRedirect(reverse_lazy("core:AdminLogin"))


@authenticated_staf
@superuser_only
def AdminUsersList(request):
    users = User.objects.all()
    print('AdminUsersList')
    if request.method == 'POST':
        user_form = AdminUserSignUpForm(request.POST)
        if user_form:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            access_level = request.POST.get('access_level')
            position = request.POST.get('position')
            is_staff = request.POST.get('is_staff')
            is_author = request.POST.get('is_author')
            is_active = request.POST.get('is_active')
            admin = request.POST.get('admin')
            print(request.POST)
            random_password = f'RD{get_random_string(5).upper()}AG{get_random_string(5).lower()}MP'
            password = make_password(random_password)
            groups = Group.objects.get_or_create(name=access_level)
            groups = Group.objects.get(name=access_level)
            user_object = User.objects.create(email=email, first_name=first_name, last_name=last_name, phone=phone,
                                              password=password,
                                              access_level=access_level, position=position, is_staff=is_staff,
                                              is_author=is_author, is_active=is_active, admin=admin,
                                              groups=groups)

            user_object.save()
            try:
                notify_user(request, first_name, email, phone, _(f'Your Account In Law Hup Created Successfully'),
                            f'Account With Mail {email} & Password {random_password}', None, 'Your Account',
                            'carehup.com', None, None)
            except:
                pass
            messages.success(request, 'User created successfully', extra_tags='User')
            return redirect('core:AdminUserList')
        else:
            messages.error(request, 'User not created', extra_tags='User')
            context = {
                'users': users,
                'user_form': user_form,
                'current_page': _('Users')

            }
            return render(request, f'{BACKEND_TEMPLATES}/account/user/admin.html', context)

    context = {
        'users': users,
        'user_form': AdminUserSignUpForm(),
        'current_page': _('Users')

    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/admin.html', context)


@authenticated_staf
@admin_only
def AdminUserDetail(request, slug):
    current_user = get_object_or_404(User, slug=slug)
    user_form = UserUpdateForm()
    context = {
        'current_user': current_user,
        'user_form': user_form
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/details.html', context)


class AdminUserCreate(CreateView):
    model = User

    form_class = AdminUserSignUpForm
    template_name = f'{BACKEND_TEMPLATES}/account/user/admin.html'
    success_url = reverse_lazy('core:AdminUserList')

    @method_decorator(authenticated_staf, admin_only)
    def dispatch(self, *args, **kwargs):
        return super(AdminUserCreate, self).dispatch(*args, **kwargs)


@authenticated_staf
@admin_only
def AdminUserUpdate(request, slug):
    try:
        if current_user := User.objects.get(slug=slug):
            profile = UserProfile.objects.get(user=current_user)
            admin = request.user
            if not admin.is_superuser and current_user != request.user:
                return redirect('core:AdminError403')
            user_form = AdminUserUpdateForm(request.POST, request.FILES, instance=current_user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)


            if request.method == 'POST':

                try:
                    if user_form.is_valid() or profile_form.is_valid():
                        image = request.FILES.get('image')
                        first_name = request.POST.get('first_name')
                        last_name = request.POST.get('last_name')
                        phone = request.POST.get('phone')
                        access_level = request.POST.get('access_level')
                        is_active = request.POST.get('is_active')
                        is_superuser = request.POST.get('is_superuser')
                        admin = request.POST.get('admin')
                        author = request.POST.get('author')
                        is_staff = request.POST.get('is_staff')
                        groups = request.POST.get('groups')
                        country = None
                        country_id = request.POST.get('country')

                        if country_id not in ['', None]:
                            country = Country.objects.get(id=country_id)
                        lang_id = request.POST.get('lang')
                        lang = Language.objects.get(id=lang_id) if lang_id not in ['', None] else None
                        user_object = User.objects.get(slug=slug)
                        user_object.first_name = first_name
                        user_object.last_name = last_name
                        user_object.phone = phone
                        user_object.access_level = access_level
                        if image != None:
                            user_object.image = image
                        if is_active != None:
                            user_object.is_active = is_active
                        if is_superuser != None:
                            user_object.is_superuser = is_superuser
                        if admin != None:
                            user_object.admin = admin
                        if is_staff != None:
                            user_object.is_staff = is_staff
                        if author != None:
                            user_object.is_author = author
                        user_object.save()
                        user_object.groups.add(groups)
                        user_profile = UserProfile.objects.get(user=current_user)
                        if country_id not in ['', None]:
                            user_profile.country = country
                        if lang_id not in ['', None]:
                            user_profile.lang = lang
                        user_profile.save()
                        print(3)
                        return redirect(request.META['HTTP_REFERER'])

                except Exception as e:

                    messages.error(request, _("Please Fill All Data"))
                    print(4)
            else:
                context = {
                    'current_user': current_user,
                    'profile': profile,
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'current_page': _('Update'),
                    'prev_Page': _('All User'),
                    'prev_Page_link': reverse_lazy('core:AdminUserList'),
                }
                return render(request, f'{BACKEND_TEMPLATES}/account/user/update.html', context)
            context = {
                'current_user': current_user,
                'profile': profile,
                'user_form': user_form,
                'profile_form': profile_form,
                'current_page': _('Update'),
                'prev_Page': _('All User'),
                'prev_Page_link': reverse_lazy('core:AdminUserList'),
            }
            return render(request, f'{BACKEND_TEMPLATES}/account/user/update.html', context)
    except ObjectDoesNotExist as e:
        return redirect('core:AdminError404')


@authenticated_staf
@staff_only
def AdminUserChangePassword(request, slug):
    current_user = User.objects.get(slug=slug)
    admin = request.user

    if admin or current_user == request.user:

        form = PasswordChangeForm


        if request.method == 'POST':
            form = PasswordChangeForm(current_user, request.POST)
            if form:
                new_password1 = request.POST.get('new_password1')
                new_password2 = request.POST.get('new_password2')
                if new_password1 != new_password2:
                    messages.error(request, 'Password and Confirm Password Not Match', extra_tags='User')
                    return redirect(request.META['HTTP_REFERER'], {'form': form})

                current_user.set_password(request.POST.get('new_password1'))
                current_user.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, 'Your password was successfully updated!', extra_tags='User')
                return redirect(request.META['HTTP_REFERER'], {'form': form})
            else:
                messages.error(request, 'Please correct the error below.', extra_tags='User')
                form = PasswordChangeForm(current_user,)
        else:
            form = PasswordChangeForm(current_user,)
        return redirect(request.META['HTTP_REFERER'], {'form': form})
    else:
        return redirect('core:AdminError403')


@authenticated_staf
@staff_only
def AdminUserAccountSettings(request, slug):
    current_user = User.objects.get(slug=slug)

    if current_user.id == request.user.id:

        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=current_user)
        profile = UserProfile.objects.get(user=current_user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if request.method == 'POST':
            if user_form:
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                phone = request.POST.get('phone')
                image = request.FILES.get('image')
                country_id = request.POST.get('country')
                lang_id = request.POST.get('lang')
                try:
                    country = Country.objects.get(id=country_id)
                except Exception as e:
                    country = None
                try:
                    lang = Language.objects.get(id=lang_id)
                except Exception as e:
                    lang = None

                user_object = User.objects.get(slug=slug)
                user_object.first_name = first_name
                user_object.last_name = last_name
                user_object.phone = phone
                if image:
                    user_object.image = image
                else:
                    user_object.image = user_object.image
                user_object.save()

                user_profile = UserProfile.objects.get(user=current_user)
                user_profile.country = country
                user_profile.lang = lang
                user_profile.save()
                print(3)
                messages.success(request, _("Your Profile Updated Successfully"), extra_tags='User')
                return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, _("Please Fill All Data"), extra_tags='User')
                return redirect(request.META['HTTP_REFERER'])
        else:
            context = {
                'current_user': current_user,
                'profile': profile,
                'user_form': user_form,
                'profile_form': profile_form,
                'password_form': PasswordChangeForm(request.user),
            }
            return render(request, f'{BACKEND_TEMPLATES}/account/user/setting.html', context)
    else:
        return redirect('core:AdminError403')


@authenticated_staf
@staff_only
def UserPublicProfile(request, slug, *args, **kwargs):
    user = User.objects.get(slug=slug)
    suggestions_user = User.objects.all()

    setting_form = UserProfileForm(instance=user)
    context = {}
    user_slug = kwargs.get("slug")
    try:
        account = User.objects.get(slug=slug)
    except:
        return HttpResponse("Something went wrong.")
    if account:
        context['id'] = account.id

        context['email'] = account.email
        if user.image:
            context['profile_image'] = user.image.url
        context['hide_email'] = user.hide_email

        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends'] = friends

        # Define template variables
        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value  # range: ENUM -> friend/friend_request_status.FriendRequestStatus
        friend_requests = None
        user = request.user
        if user.is_authenticated and user != account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
                # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
                if get_friend_request_or_false(sender=account, receiver=user) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
                # CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
                elif get_friend_request_or_false(sender=user, receiver=account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                # CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except:
                pass

        context = {
            'user': user,
            'suggestions_user': suggestions_user,
            'setting_form': setting_form,
            'is_self': is_self,
            'is_friend': is_friend,
            'request_sent': request_sent,
            'friend_requests': friend_requests,
            'BASE_URL': settings.BASE_URL,

        }

    return render(request, f'{BACKEND_TEMPLATES}/account/user/profile.html', context)


@authenticated_staf
@staff_only
def UserStatements(request, slug):
    user = User.objects.get(slug=slug)
    setting_form = UserProfileForm(instance=user)
    context = {
        'user': user,
        'setting_form': setting_form
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/statements.html', context)


@authenticated_staf
@staff_only
def UserBilling(request, slug):
    user = User.objects.get(slug=slug)
    setting_form = UserProfileForm(instance=user)
    context = {
        'user': user,
        'setting_form': setting_form
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/billing.html', context)


@authenticated_staf
@staff_only
def UserReferrals(request, slug):
    if slug == '':
        return redirect('core:AdminError404')
    else:
        user = User.objects.get(slug=slug)
        setting_form = UserProfileForm(instance=user)
        context = {
            'user': user,
            'setting_form': setting_form
        }
        return render(request, f'{BACKEND_TEMPLATES}/account/user/referrals.html', context)


@authenticated_staf
@staff_only
def UserDarkModeUpdate(request, ):
    user = User.objects.get(id=request.user.id)
    setting = UserProfile.objects.get_or_create(user=user)
    user_mode = UserProfile.objects.get(user=user)

    mode = UserProfile.objects.get(user=user).dark_mode
    if mode == 'Active':
        dark_mode = 'Inactive'
    elif mode == 'Inactive':
        dark_mode = 'Active'
    user_mode.dark_mode = dark_mode
    user_mode.save()
    return redirect(request.META['HTTP_REFERER'])


@authenticated_staf
@staff_only
def AdminUserDeactivate(request, slug):
    user = User.objects.get(id=request.user.id, slug=slug)
    if request.method == 'POST':
        deactivate = request.POST.get('deactivate')
        print('deactivate', deactivate)
        if deactivate != 'Deactivate':
            return redirect(request.META['HTTP_REFERER'])
        user.is_active = False
        user.save()
        return redirect('home:HomeIndex')
    return redirect(request.META['HTTP_REFERER'])


@authenticated_staf
@superuser_only
def AdminUserDelete(request, slug):
    current_user = request.user
    if current_user.is_superuser:
        user = User.objects.get(slug=slug)
        print('user', user)
        if request.method == 'POST':
            user.delete()

            messages.success(request, _("user account was successfully deleted"), extra_tags='User')
            return HttpResponseRedirect(reverse_lazy('core:AdminUserList'))
        else:

            messages.error(request, _("user account was not deleted!"), extra_tags='User')
            return HttpResponseRedirect(reverse_lazy('core:AdminUserList'))
    else:

        messages.error(request, _("You are not authorized to delete this user account!"), extra_tags='User')
        return HttpResponseRedirect(reverse_lazy('core:AdminUserList'))


############################ Admin User Group ###################
@authenticated_staf
@superuser_only
def AdminUserGroupList(request):
    groups = Group.objects.all()
    context = {
        'groups': groups,
        'current_page': _('User Group')
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/group/admin.html', context)


@authenticated_staf
@superuser_only
def AdminUserGroupCreate(request):
    if request.method == 'POST':
        group_form = AdminGroupForm(request.POST)
        if group_form.is_valid():
            name = request.POST.get('name')
            permissions = request.POST.get('permissions')
            group_object = group_form.save(commit=False)
            group_object.name = name
            group_object.permissions = permissions
            group_object.save()
            messages.success(request, 'Group created successfully', extra_tags='Group')
            return redirect('core:AdminUserGroupList')
        else:
            messages.error(request, 'Group not created', extra_tags='Group')
            context = {
                'group_form': group_form,
                'current_page': _('User Group')
            }
            return render(request, f'{BACKEND_TEMPLATES}/account/group/create.html', context)

    context = {
        'group_form': AdminGroupForm(),
        'current_page': _('User Group')
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/group/create.html', context)


@authenticated_staf
@superuser_only
def AdminUserGroupEdit(request, slug):
    try:
        if current_group := Group.objects.get(slug=slug):
            group_form = AdminGroupForm(request.POST or None, instance=current_group)
            if request.method == 'POST':
                if group_form.is_valid():
                    name = request.POST.get('name')
                    permissions = request.POST.get('permissions')
                    group_object = Group.objects.get(slug=slug)
                    group_object.name = name
                    group_object.permissions = permissions
                    group_object.save()
                    messages.success(request, 'Group updated successfully', extra_tags='Group')
                    return redirect('core:AdminUserGroupList')
                else:
                    messages.error(request, 'Group not updated', extra_tags='Group')
                    context = {
                        'group_form': group_form,
                        'current_page': _('User Group')
                    }
                    return render(request, f'{BACKEND_TEMPLATES}/account/group/edit.html', context)

            context = {
                'group_form': group_form,
                'current_page': _('User Group')
            }
            return render(request, f'{BACKEND_TEMPLATES}/account/group/edit.html', context)
    except ObjectDoesNotExist as e:
        return redirect('core:AdminError404')


@authenticated_staf
@superuser_only
def AdminUserGroupDelete(request, slug):
    current_user = request.user
    if current_user.is_superuser:
        group = Group.objects.get(slug=slug)
        print('group', group)
        if request.method == 'POST':
            group.delete()

            messages.success(request, _("Group was successfully deleted"), extra_tags='Group')
            return HttpResponseRedirect(reverse_lazy('core:AdminUserGroupList'))
        else:

            messages.error(request, _("Group was not deleted!"), extra_tags='Group')
            return HttpResponseRedirect(reverse_lazy('core:AdminUserGroupList'))
    else:

        messages.error(request, _("You are not authorized to delete this Group!"), extra_tags='Group')
        return HttpResponseRedirect(reverse_lazy('core:AdminUserGroupList'))


@authenticated_staf
@superuser_only
def AdminUsersGeoInfoList(request):
    users = UserGeoInfo.objects.all()
    context = {
        'users': users,
        'current_page': _('Users Geo Info')
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/geo_info.html', context)

@authenticated_staf
@superuser_only
def AdminUsersFcmTokenList(request):
    users = User.objects.all()
    devices = DeviceInfo.objects.all()
    fcm = FCMDevice.objects.all()
    # for item in fcm:
    #     item.delete()
    context = {
        'users': users,
        'devices': devices,
        'fcm': fcm,
        'current_page': _('Users Fcm Token')
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/fcm.html', context)


@authenticated_staf
@superuser_only
def AdminUsersNewsletterList(request):
    users = Newsletter.objects.all()
    context = {
        'users': users,
        'current_page': _('Users Newsletter')
    }
    return render(request, f'{BACKEND_TEMPLATES}/account/user/newsletter.html', context)


@authenticated_staf
@superuser_only
def AdminClientContactList(request):
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts,
        'current_page': _('Client Contact')
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/contact/admin.html', context)


def AdminClientContactDetail(request, slug):
    context = {}
    try:
        contact = Contact.objects.get(slug=slug)
        context['contact'] = contact
    except Contact.DoesNotExist:
        return redirect('core:AdminClientContactList')
    return render(request, f'{BACKEND_TEMPLATES}/people/contact/details.html', context)


def AdminPublicSearch(request, *args, **kwargs):
    context = {}
    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            search_results = User.objects.filter(email__icontains=search_query).filter(
                username__icontains=search_query).distinct()
            user = request.user
            accounts = []  # [(account1, True), (account2, False), ...]
            if user.is_authenticated:
                # get the authenticated users friend list
                auth_user_friend_list = FriendList.objects.get(user=user)
                for account in search_results:
                    accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
                context['accounts'] = accounts
            else:
                for account in search_results:
                    accounts.append((account, False))
                context['accounts'] = accounts

    return render(request, "good/utilities/serach/search.html", context)