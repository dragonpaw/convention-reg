from django import forms
from convention.reg.models import Person, MembershipSold, MembershipType, PaymentMethod

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
    method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
    )

    comment = forms.CharField(max_length=80, required=False, label="Comment")
