from django import forms
from convention.reg.models import Member, Membership

class MemberForm(forms.ModelForm):

    class Meta:
        model = Member

class MembershipForm(forms.ModelForm):
    member = forms.ModelChoiceField(label="Member",
                                  queryset=Member.objects.all(),
                                  widget=forms.HiddenInput())

    class Meta:
        model = Membership
        fields = ( 'type', 'payment_method')
