import json
from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractBaseUser
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import (
    DetailView,
    ListView,

)

from core.forms.chats import RoomCreationsForm
from core.models.chat import Room, Message
from core.models.social import FriendList, FriendRequest

from core.utils.friend_request_status import FriendRequestStatus, get_friend_request_or_false
from digit_sport import settings
from digit_sport.settings import  MEDIA_ROOT
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, author_only

User = get_user_model()

@authenticated_staf
@author_only
def AdminChatDrawer(request):
    rooms = Room.objects.all()
    recipients = User.objects.all()
    user_status = User.objects.get(id=request.user.id)
    user_status.last_activity=timezone.now()
    user_status.save()


    context= {
        'rooms': rooms,
        'recipients': recipients,

        'user_status':user_status,
    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/chat/users.html',context)

@authenticated_staf

def AdminChatMessenger(request):


    # messages = Message.objects.filter(room=room)[0:25]
    user_status = User.objects.get(id=request.user.id)
    user_status.last_activity = timezone.now()
    user_status.is_online=True
    user_status.save()
    recipients = User.objects.all()
    current_user = request.user
    chat_list = []
    try:
        check_user_rooms = Room.objects.filter(created_by=current_user.id).count()
        if check_user_rooms>0:

            user_rooms = Room.objects.filter(created_by=current_user.id)
        else:
            user_rooms = Room.objects.filter(recipient_two=current_user.id)

    except:
        user_rooms = Room.objects.filter(created_by=current_user.id)
    print('user_rooms',user_rooms)
    for user_room in user_rooms:
        message = Message.objects.filter(room=user_room.id).last
        message_count = Message.objects.filter(room=user_room.id).count()
        chat_list.append(
            {"user_room": user_room, "message": message, "message_count": message_count})
    recipient_list =json.dumps(list(recipients.values()),indent=4, sort_keys=True, default=str)
    base_url = MEDIA_ROOT
    print(base_url)

    context= {
        'room': room,
        # 'messages': messages,
        'chat_list':chat_list,
        'user_status':user_status,
        'recipients': recipients,
        'recipients_list':recipient_list,


    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/chat/messenger.html',context)


def account_view(request, *args, **kwargs):
    """
    - Logic here is kind of tricky
        is_self
        is_friend
            -1: NO_REQUEST_SENT
            0: THEM_SENT_TO_YOU
            1: YOU_SENT_TO_THEM
    """
    context = {}
    user_id = kwargs.get("user_id")
    try:
        account = User.objects.get(pk=user_id)
    except:
        return HttpResponse("Something went wrong.")
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.profile_image.url
        context['hide_email'] = account.hide_email

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

        # Set the template variables to the values
        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests
        context['BASE_URL'] = settings.BASE_URL
        return render(request, "account/account.html", context)



class UsersListView(LoginRequiredMixin, ListView):
    http_method_names = ['get', ]

    def get_queryset(self):
        return User.objects.all().exclude(id=self.request.user.id)

    def render_to_response(self, context, **response_kwargs):
        users: List[AbstractBaseUser] = context['object_list']

        data = [{
            "username": user.get_username(),
            "pk": str(user.pk)
        } for user in users]
        return JsonResponse(data, safe=False, **response_kwargs)


class SelfInfoView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        return self.request.user

    def render_to_response(self, context, **response_kwargs):
        user: AbstractBaseUser = context['object']
        data = {
            "username": user.get_username(),
            "pk": str(user.pk)
        }
        return JsonResponse(data, **response_kwargs)

#
# # 2.5MB - 2621440
# # 5MB - 5242880
# # 10MB - 10485760
# # 20MB - 20971520
# # 50MB - 5242880
# # 100MB 104857600
# # 250MB - 214958080
# # 500MB - 429916160
# # MAX_UPLOAD_SIZE = getattr(settings, 'MAX_FILE_UPLOAD_SIZE', 5242880)
#
# class UploadForm(ModelForm):
#     # TODO: max file size validation
#     # def check_file(self):
#     #     content = self.cleaned_data["file"]
#     #     content_type = content.content_type.split('/')[0]
#     #     if (content._size > MAX_UPLOAD_SIZE):
#     #         raise forms.ValidationError(_("Please keep file size under %s. Current file size %s")%(filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(content._size)))
#     #     return content
#     #
#     # def clean(self):
#
#     class Meta:
#         model = UploadedFile
#         fields = ['file']
#
#
# class UploadView(LoginRequiredMixin, CreateView):
#     http_method_names = ['POST', ]
#     model = UploadedFile
#     form_class = UploadForm
#
#
#     def form_valid(self, form: UploadForm):
#         self.object = UploadedFile.objects.create(uploaded_by=self.request.user, file=form.cleaned_data['file'])
#         return JsonResponse(serialize_file_model(self.object))
#
#     def form_invalid(self, form: UploadForm):
#         context = self.get_context_data(form=form)
#         errors_json: str = context['form'].errors.get_json_data()
#         return HttpResponseBadRequest(content=json.dumps({'errors': errors_json}))
#
#
#
#
#
# ############### another
# import json
# from django.core import serializers
# from django.shortcuts import render
#
# from django.contrib.auth.models import User
# from django.utils.safestring import mark_safe
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
#
#
# @login_required
# def ChatIndex(request):
#     return render(request, 'good/chat/old/chatRoomIndex.html', {})
#
#
# @login_required
# def room(request, room_name):
#     return render(request, 'good/chat/old/chatRoom.html', {
#         'room_name_json': mark_safe(json.dumps(room_name)),
#         'current_user': mark_safe( serializers.serialize('json', [ request.user ] ) ),
#     })
#
#
# @login_required
# def messages(request):
#     return render(request, 'good/chat/old/messages.html', {
#         'users':   mark_safe( serializers.serialize('json', User.objects.all() ) ),
#         'current_user': mark_safe( serializers.serialize('json', [ request.user ] ) ),
#         'messages': mark_safe( serializers.serialize('json', [] ) ),
#     })
#
# @login_required
# def message(request, selected_user):
#     user1 = User.objects.get(pk=selected_user)
#     user2 = User.objects.get(pk=request.user.pk)
#     messages = MessageModel.objects.filter(sender=user1, recipient=user2) | MessageModel.objects.filter(sender=user2, recipient=user1)
#     return render(request, 'good/chat/old/messages.html', {
#         'users':   mark_safe( serializers.serialize('json', User.objects.all() ) ),
#         'current_user': mark_safe( serializers.serialize('json', [ request.user ] ) ),
#         'selected_user': mark_safe( serializers.serialize('json', [ User.objects.get(pk=selected_user) ] ) ),
#         'messages': mark_safe( serializers.serialize('json', messages.order_by('created_at') ) ),
#     })
#
# @login_required
# def messagesApi(request):
#     current_user = User.objects.get(pk=request.user.pk)
#     messages = MessageModel.objects.filter(sender=current_user) | MessageModel.objects.filter(recipient=current_user)
#     json_response = {
#         'users': json.loads(serializers.serialize('json', User.objects.all(), fields=('first_name', 'last_name'))),
#         'messages': json.loads(serializers.serialize('json', messages.order_by('created_at')[:10])),
#     }
#     return JsonResponse(json_response)
#
# @login_required
# def messageApi(request, selected_user):
#     user1 = User.objects.get(pk=selected_user)
#     user2 = User.objects.get(pk=request.user.pk)
#     messages = MessageModel.objects.filter(sender=user1, recipient=user2) | MessageModel.objects.filter(sender=user2, recipient=user1)
#     json_response = {
#         'users':   json.loads( serializers.serialize('json', User.objects.all() ) ),
#         'current_user': json.loads( serializers.serialize('json', [ request.user ] ) ),
#         'selected_user': json.loads( serializers.serialize('json', [ User.objects.get(pk=selected_user) ] ) ),
#         'messages': json.loads( serializers.serialize('json', messages.order_by('created_at') ) ),
#     }
#     return JsonResponse(json_response)




@login_required
def rooms(request):
    my_rooms = request.user.created_rooms.all()
    rooms = Room.objects.all().exclude(id__in=my_rooms.values_list('id', flat=True))
    context = {'my_rooms': my_rooms, 'rooms': rooms}

    return render(request, f'{BACKEND_TEMPLATES}/utilities/chat/rooms.html', context)


@login_required
def room(request, pk):
    room = get_object_or_404(Room, pk=1)
    print('room', room)
    websocket_url = request.get_host() + '/room/' + room.name + '/'

    if room.private_room:
        if request.method == 'POST':
            passcode = request.POST.get('auth_passcode')
            if room.check_passcode(passcode):

                return render(request, f'{BACKEND_TEMPLATES}/chat/room.html', context={'room': room, 'websocket_url': websocket_url})
            else:
                error_message = '!! Incorrect Passcode !!'

                return render(request, f'{BACKEND_TEMPLATES}/chat/private_room.html',
                              context={'room': room, 'error_message': error_message})
        else:
            error_message = ''
            return render(request, f'{BACKEND_TEMPLATES}/chat/private_room.html',
                          context={'room': room, 'error_message': error_message})
    else:
         return render(request, f'{BACKEND_TEMPLATES}/utilities/chat/room.html', context={'room': room, 'websocket_url': websocket_url})


@login_required
def create_room(request):
    form = RoomCreationsForm(request.POST or None)
    if form.is_valid():
        room = form.save(commit=False)
        room.created_by = request.user
        room.save()
        return redirect('core:room', pk=room.pk)


    return render(request, f'{BACKEND_TEMPLATES}/chat/create_room.html', {'form': form})


@login_required
def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.user != room.created_by:
        return redirect('rooms')

    if request.method == 'POST':
        if 'passcode' in request.POST:
            form = RoomCreationsForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                return redirect('rooms')
        else:
            passcode = request.POST.get('auth_passcode')
            if not room.check_passcode(passcode):
                error_message = '!! Incorrect Passcode !!'
                return render(request, 'chat/private_room.html', context={'room': room, 'error_message': error_message})

        form = RoomCreationsForm(instance=room)
    else:
        form = RoomCreationsForm(instance=room)

        if room.private_room:
            error_message = ''
            return render(request, 'chat/private_room.html', context={'room': room, 'error_message': error_message})

    return render(request, 'chat/edit_room.html', {'form': form, 'room': room})

@login_required
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('rooms')
    return render(request, 'chat/delete_room.html', {'room': room})