from django import forms
from convention.reg.models import Member, Membership, MembershipType, PaymentMethod

class MemberForm(forms.ModelForm):

    birth_date = forms.DateField(('%d/%m/%y',), label = "Birth Date", required=False,
        widget=forms.DateInput(format='%d/%m/%y', attrs={'class':'input'}),
    )

    class Meta:
        model = Member


class MembershipForm(forms.ModelForm):
    member = forms.ModelChoiceField(
        label="Member",
        queryset=Member.objects.all(),
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
        model = Membership
        fields = ( 'type', 'payment_method')
