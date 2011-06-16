from django import forms
from convention.reg.models import Person, MembershipSold, MembershipType, PaymentMethod
from datetime import date

import fields

CURRENT_YEAR = date.today().year
MAX_YEARS = 12

class MemberForm(forms.ModelForm):

    birth_date = forms.DateField(
        label = "Birth Date",
        required=False,
        help_text='mm/dd/yyyy',
        widget=forms.DateInput(format='%m/%d/%Y', attrs={'class':'input'}),
    )

    class Meta:
        model = Person


class SelfServeAddMemberForm(forms.ModelForm):
    birth_date = forms.DateField(
        label = "Birth Date",
        required=False,
        help_text='mm/dd/yyyy',
        widget=forms.DateInput(format='%m/%d/%Y', attrs={'class':'input'}),
    )

    class Meta:
        model = Person

class MembershipForm(forms.ModelForm):
    member = forms.ModelChoiceField(
        label="Person",
        queryset=Person.objects.all(),
        widget=forms.HiddenInput(),
    )


    type = forms.ModelChoiceField(
        label = "Type",
        queryset = MembershipType.objects.available(),
    )

    payment_method = forms.ModelChoiceField(
        label="Method",
        queryset=PaymentMethod.objects.all(),
    )

    class Meta:
        model = MembershipSold
        fields = ('type', 'quantity')


class SelfServeAddMembershipForm(forms.Form):
    type_choices = [
        (x.pk, '{0}: ${1}'.format(x,x.price)) for x in MembershipType.objects.available(public=True)
    ]

    type = forms.ChoiceField(
        label = "Type",
        choices = type_choices,
    )

    quantity = forms.IntegerField(
        min_value = 1, max_value = 999,
        initial = 1
    )

    def clean(self):
        cleaned = self.cleaned_data
        type = MembershipType.objects.get(pk=cleaned.get('type'))
        quantity = cleaned.get('quantity')
        if quantity > 1 and not type.in_quantity:
            self.data = self.data.copy()
            self.data['quantity'] = 1
            self._errors["quantity"] = self.error_class(['You cannot buy multiple of that type.'])
            del cleaned['quantity']
        return cleaned


class SelfServePaymentForm(forms.Form):
    name = forms.CharField(label="Name on Card", max_length=60)
    address = forms.CharField(label="Billing Address", max_length=60)
    zip = forms.IntegerField(
        label='Billing Zip',
        min_value=00000, max_value=99999,
        required = False,
    )
    email = forms.EmailField(help_text='Receipt will be emailed.')

    number = fields.CreditCardNumberField(label='Card #')
    expires = fields.MonthYearField()
    cvv = forms.IntegerField(
        label = 'CVV (On the back)',
        min_value=0000, max_value=9999,
        required = False,
    )


class PaymentForm(forms.Form):
    comment = forms.CharField(max_length=80, required=False, label="Comment")
    method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
    )

    number = fields.CreditCardNumberField(label='Credit Card #', required=False)

    #number = forms.CharField(
    #    label="Credit Card #",
    #    max_length = 20,
    #    required = False,
    #)

    expires = fields.MonthYearField()

    cvv = forms.IntegerField(
        label = 'CVV (On the back)',
        min_value=0000, max_value=9999,
        required = False,
    )
    zip = forms.IntegerField(
        min_value=00000, max_value=99999,
        required = False,
    )

    def clean_number(self):
        data = self.cleaned_data['number'].strip()
        data = data.replace(' ','')
        data = data.replace('-','')
        return data

    def clean(self):
        cleaned = self.cleaned_data
        method = cleaned.get('method')
        if method.gateway == 'cash':
            return cleaned
        else:
            for field in ('number', 'month', 'year', 'cvv', 'zip'):
                if not cleaned.get(field):
                    self._errors[field] = self.error_class(['Required for CC processing.'])
        return cleaned
