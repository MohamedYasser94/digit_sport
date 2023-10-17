from rest_framework import permissions

from core.models.team import ProjectMembership


class CanViewBoard(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.can_view_board(obj)


class IsAuthorOrReadOnly(CanViewBoard):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return super().has_object_permission(request, view, obj.item.list.board)
        else:
            return request.user == obj.author


class IsProjectAdminOrMemberReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            pmem = ProjectMembership.objects.get(member=request.user, project=obj)
        except ProjectMembership.DoesNotExist:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        return pmem.access_level == 2


class IsProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            pmem = ProjectMembership.objects.get(member=request.user, project=obj)
        except ProjectMembership.DoesNotExist:
            return False
        return True


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user