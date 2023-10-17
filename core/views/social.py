from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from core.models.social import FriendList, FriendRequest
from core.utils.friend_request_status import FriendRequestStatus
from core.utils.notification import create_notification_chat
from digit_sport import settings
from helper.decorators import authenticated_staf
from user.models import User


# User = get_user_model()


@authenticated_staf
def AdminUserFollower(request, slug, *args, **kwargs):
    """
    	- Logic here is kind of tricky
    		is_self
    		is_friend
    			-1: NO_REQUEST_SENT
    			0: THEM_SENT_TO_YOU
    			1: YOU_SENT_TO_THEM
    	"""
    context = {}
    user_slug = kwargs.get("slug")
    try:
        this_account = User.objects.get(slug=slug)
    except Exception as e:
       
        return HttpResponse("Something went wrong.")
    if this_account:
        context['this_account'] = this_account
        receiver=FriendRequest.objects.filter(sender=this_account,)
        suggestions = User.objects.exclude(receiver__in=receiver)
        suggestions_friends = list(suggestions.values('id', 'email', 'slug'))
        context['suggestions_friends'] = suggestions
        try:
            friend_list = FriendList.objects.get(user=this_account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=this_account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends'] = friends

        # Define template variables
        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value  # range: ENUM -> friend/friend_request_status.FriendRequestStatus
        friend_requests = None
        user = request.user
        if user.is_authenticated and user != this_account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
                # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
                if FriendRequest.objects.get(sender=this_account, receiver=user) != False:

                    context['follow_request'] = FriendRequest.objects.filter(sender=this_account, receiver=user)
                # CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
                elif FriendRequest.objects.filter(sender=user, receiver=this_account) != False:

                    context['request_send'] = FriendRequest.objects.filter(sender=user)
                # CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT


        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
                print('friend_requests', friend_requests)
            except:
                pass

        # Set the template variables to the values
        context['this_user'] = request.user
        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests

        context['BASE_URL'] = settings.BASE_URL

    return render(request, "good/account/social/followers.html", context)


def friend_requests(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        account = User.objects.get(pk=user_id)
        if account == user:
            friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
            context['friend_requests'] = friend_requests
        else:
            return HttpResponse("You can't view another users friend requets.")
    else:
        redirect("login")
    return render(request, "good/account/social/followers.html", context)


def send_friend_request(request, slug, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        if user_slug := User.objects.get(slug=slug):
            print('user slug ', user_slug)
            receiver = User.objects.get(slug=slug)
            try:
                # Get any friend requests (active and not-active)
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                # find if any of them are active (pending)
                try:
                    for request in friend_requests:
                        if request.status == 'SENT':
                            raise Exception("You already sent them a friend request.")
                    # If none are active create a new friend request
                    friend_request = FriendRequest(sender=user, receiver=receiver, status='SENT')
                    friend_request.save()


                    create_notification_chat(request, receiver, user,friend_request.id )
                    payload['response'] = "Friend request sent."
                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExist:
                # There are no friend requests so create one.
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                payload['response'] = "Friend request sent."

            if payload['response'] is None:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Unable to sent a friend request."
    else:
        payload['response'] = "You must be authenticated to send a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


def accept_friend_request(request, slug, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "GET" and user.is_authenticated:
        if user_slug := User.objects.get(slug=slug):
            print('slug', slug)
            receiver = User.objects.get(slug=slug)
            sender = User.objects.get(slug=request.user.slug)
            friend_request = FriendRequest.objects.get(receiver=receiver)

            # confirm that is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request. Now accept it
                    friend_request.add(receiver)
                    friend_request.add(user)
                    # updated_notification = friend_request.accept()
                    payload['response'] = "Friend request accepted."

                else:
                    payload['response'] = "Something went wrong."
            else:
                payload['response'] = "That is not your request to accept."
        else:
            payload['response'] = "Unable to accept that friend request."
    else:
        # should never happen
        payload['response'] = "You must be authenticated to accept a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


def remove_friend(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        if user_id := request.POST.get("receiver_user_id"):
            try:
                removee = User.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['response'] = "Successfully removed that friend."
            except Exception as e:
                payload['response'] = f"Something went wrong: {str(e)}"
        else:
            payload['response'] = "There was an error. Unable to remove that friend."
    else:
        # should never happen
        payload['response'] = "You must be authenticated to remove a friend."
    return HttpResponse(json.dumps(payload), content_type="application/json")


def decline_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "GET" and user.is_authenticated:
        if friend_request_id := kwargs.get("friend_request_id"):
            friend_request = FriendRequest.objects.get(pk=friend_request_id)

            # confirm that is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request. Now decline it
                    updated_notification = friend_request.decline()
                    payload['response'] = "Friend request declined."
                else:
                    payload['response'] = "Something went wrong."
            else:
                payload['response'] = "That is not your friend request to decline."
        else:
            payload['response'] = "Unable to decline that friend request."
    else:
        # should never happen
        payload['response'] = "You must be authenticated to decline a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


def cancel_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        if user_id := request.POST.get("receiver_user_id"):
            receiver = User.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
            except FriendRequest.DoesNotExist:
                payload['response'] = "Nothing to cancel. Friend request does not exist."

            # There should only ever be ONE active friend request at any given time. Cancel them all just in case.
            if len(friend_requests) > 1:
                for request in friend_requests:
                    request.cancel()
            else:
                # found the request. Now cancel it
                friend_requests.first().cancel()
            payload['response'] = "Friend request canceled."
        else:
            payload['response'] = "Unable to cancel that friend request."
    else:
        # should never happen
        payload['response'] = "You must be authenticated to cancel a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")
