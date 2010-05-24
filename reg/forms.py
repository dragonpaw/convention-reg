from django import forms
from convention.reg.models import Person, MembershipSold, MembershipType, PaymentMethod
from datetime import date
CURRENT_YEAR = date.today().year
MAX_YEARS = 12

class MemberForm(forms.ModelForm):

    birth_date = forms.DateField(('%m/%d/%y',), label = "Birth Date", required=False,
        widget=forms.DateInput(format='%m/%d/%y', attrs={'class':'input'}),
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
        fields = ( 'type', 'payment_method')


class PaymentForm(forms.Form):
    comment = forms.CharField(max_length=80, required=False, label="Comment")
    method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
    )
    number = forms.CharField(
        label="Credit Card #",
        max_length = 20,
        required = False,
    )
    month = forms.TypedChoiceField(
        coerce=int,
        choices=(
            ('1', '01: January'),
            ('2', '02: February'),
            ('3', '03: March'),
            ('4', '04: April'),
            ('5', '05: May'),
            ('6', '06: June'),
            ('7', '07: July'),
            ('8', '08: August'),
            ('8', '09: September'),
            ('10', '10: October'),
            ('11', '11: November'),
            ('12', '12: December'),
        )
    )
    year = forms.TypedChoiceField(
        coerce=int,
        choices = [(x,x) for x in range(CURRENT_YEAR,CURRENT_YEAR+MAX_YEARS)]
    )
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
