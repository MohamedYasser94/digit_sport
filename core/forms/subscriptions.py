from django import forms

from core.models.subscriptions import Coupon, Membership, Subscription


class AdminCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        exclude = ['user','coupon','slug','used_at','status']


class AdminMembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = '__all__'
        # exclude = ['user','coupon','slug','used_at','status']



class AdminSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        #fields = '__all__'
        exclude = ['code','slug','active']
