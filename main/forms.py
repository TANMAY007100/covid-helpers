from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
import re
from django import forms
import logging
from django.core.validators import RegexValidator, EmailValidator
from django.forms.forms import Form
from .models import User

logger = logging.getLogger('general')

PROVIDER_CHOICES = [('oxygen', 'Oxygen'), ('freefood', 'Free Food'), ('plasma', 'Plasma')]
CONSUMER_CHOICES = [('oxygen', 'Oxygen'), ('freefood', 'Free Food'), ('plasma', 'Plasma')]

phone_number_regex = '\d{10}'

phone_number_regex_compiled = re.compile(phone_number_regex)

phone_number_validator = RegexValidator(phone_number_regex_compiled, message="Phone number can only be digits")

class RegistrationForm(UserCreationForm):

    phone_number = forms.CharField(max_length=255, validators=[phone_number_validator])
    location = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255, validators=[EmailValidator])
    provider_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=PROVIDER_CHOICES, required=False)
    consumer_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CONSUMER_CHOICES, required=False)

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_phone_number(self) -> None:
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) < 10 or len(phone_number) > 10:
            raise forms.ValidationError('Phone number must be of 10 digits', code='phone_number_too_long')
        return phone_number

    def clean_email(self) -> None:
        clean_email = self.cleaned_data['email']
        sanitized_email = clean_email.lower()
        is_exists = User.objects.filter(email=sanitized_email).exists()
        if is_exists:
            raise forms.ValidationError('A user with that email already exists', code='email_exists')
        return sanitized_email


class SignInForm(AuthenticationForm):

    username = UsernameField(label="Email ID or Phone Number or Username",
                             widget=forms.TextInput(attrs={'autofocus': True}))


class ProfileForm(Form):

    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    phone_no = forms.CharField(max_length=255, validators=[phone_number_validator])
    email = forms.EmailField(max_length=255, validators=[EmailValidator])
    location = forms.CharField(max_length=255)
    address_line_1 = forms.CharField(max_length=255)
    address_line_2 = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    pincode = forms.CharField(max_length=255)
    provider_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=PROVIDER_CHOICES, required=False)
    consumer_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CONSUMER_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

    def clean_phone_no(self) -> None:
        phone_no = self.cleaned_data['phone_no']
        if len(phone_no) < 10 or len(phone_no) > 10:
            raise forms.ValidationError('Phone number must be of 10 digits', code='phone_number_too_long')
        return phone_no

    def clean_email(self) -> None:
        clean_email = self.cleaned_data['email']
        sanitized_email = clean_email.lower()
        is_exists = User.objects.exclude(id=self.user_id).filter(email=sanitized_email).exists()
        if is_exists:
            raise forms.ValidationError('A user with that email already exists', code='email_exists')
        return sanitized_email
