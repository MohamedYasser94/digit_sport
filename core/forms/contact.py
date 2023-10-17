# Create your forms here.
from django import forms
import re
from core.models.services import Contact, Newsletter, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'

class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = '__all__'
class ContactSendPhoneForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['phone',]

    default_error_messages = {
        'invalid': 'Please enter a valid Egypt phone number.',
    }

    def __init__(self, *args, **kwargs):
        super(ContactSendPhoneForm, self).__init__(*args, **kwargs)
        self.regex = re.compile(r'^01[0-2][0-9]{8}$')  # Regex pattern for Egypt phone number

    def clean(self, phone):
        phone = super(ContactSendPhoneForm, self).clean(phone)
        if phone:
            if not self.regex.match(phone):
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return phone

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = '__all__'