import datetime

from django import forms

class MonthYearWidget(forms.MultiWidget):
    """
    A widget that splits a date into Month/Year with selects.
    """
    def __init__(self, attrs=None):
        months = (
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

        year = int(datetime.date.today().year)
        years = [(y, y) for y in range(year, year+11)]

        widgets = (
            forms.Select(attrs=attrs, choices=months),
            forms.Select(attrs=attrs, choices=years)
        )
        super(MonthYearWidget, self).__init__(widgets, attrs)


    def decompress(self, value):
        if value:
            return [value.month, value.year]
        else:
            return [None, None]


    def render(self, name, value, attrs=None):
        try:
            value = datetime.date(month=int(value[0]), year=int(value[1]), day=1)
        except:
            value = ''
        return super(MonthYearWidget, self).render(name, value, attrs)


class MonthYearField(forms.MultiValueField):
    widget=MonthYearWidget

    def compress(self, data_list):
        if data_list:
            return datetime.date(year=int(data_list[1]), month=int(data_list[0]), day=1)
        else:
            return datetime.date.today()

    def __init__(self, *args, **kwargs):
        forms.MultiValueField.__init__(self, *args, **kwargs)
        self.fields = (forms.CharField(), forms.CharField(),)


"""
    Provides functions & Fields for validating credit card numbers
    Thanks to David Shaw for the Luhn Checksum code
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/172845)
"""


import re

def ValidateLuhnChecksum(number_as_string):
    """ checks to make sure that the card passes a luhn mod-10 checksum """

    sum = 0
    num_digits = len(number_as_string)
    oddeven = num_digits & 1

    for i in range(0, num_digits):
        digit = int(number_as_string[i])

        if not (( i & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    return ( (sum % 10) == 0 )

# Regex for valid card numbers
CC_PATTERNS = {
    'mastercard':   '^5[12345]([0-9]{14})$',
    'visa':         '^4([0-9]{12,15})$',
    'amex':         '^3[47][0-9]{13}$',
    'discover':     '^6(?:011|5[0-9]{2})[0-9]{12}$',
}

def ValidateCharacters(number):
    """ Checks to make sure string only contains valid characters """
    return re.compile('^[0-9 ]*$').match(number) != None

def StripToNumbers(number):
    """ remove spaces from the number """
    if ValidateCharacters(number):
        result = ''
        rx = re.compile('^[0-9]$')
        for d in number:
            if rx.match(d):
                result += d
        return result
    else:
        raise Exception('Number has invalid digits')

def ValidateDigits(type, number):
    """ Checks to make sure that the Digits match the CC pattern """
    regex = CC_PATTERNS.get(type.lower(), False)
    if regex:
        return re.compile(regex).match(number) != None
    else:
        return False

def ValidateCreditCard(type, number):
    """ Check that a credit card number matches the type and validates the Luhn Checksum """
    type = type.strip().lower()
    if ValidateCharacters(number):
        number = StripToNumbers(number)
        if CC_PATTERNS.has_key(type):
            return ValidateDigits(type, number)
            return ValidateLuhnChecksum(number)   # BUG: Never reached!
    return False

class CreditCardNumberField(forms.CharField):
    """ A newforms widget for a creditcard number """
    def clean(self, value):

        value = forms.CharField.clean(self, value)
        if not ValidateCharacters(value):
            raise forms.ValidationError('Can only contain numbers and spaces.')
        value = StripToNumbers(value)
        if not ValidateLuhnChecksum(value):
            raise forms.ValidationError('Not a valid credit card number.')

        return value


#class CreditCardExpiryField(forms.CharField):
#    """ A newforms widget for a creditcard expiry date """
#    def clean(self, value):
#        value = forms.CharField.clean(self, value.strip())
#
#        # Just check MM/YY Pattern
#        r = re.compile('^([0-9][0-9])/([0-9][0-9])$')
#        m = r.match(value)
#        if m == None:
#            raise forms.ValidationError('Must be in the format MM/YY. i.e. "11/10" for Nov 2010.')
#
#        # Check that the month is 1-12
#        month = int(m.groups()[0])
#        if month < 1 or month > 12:
#            raise forms.ValidationError('Month must be in the range 1 - 12.')
#
#        # Check that the year is not too far into the future
#        year = int(m.groups()[1])
#        curr_year = datetime.datetime.now().year % 100
#        max_year = curr_year + 10
#        if year > max_year or year < curr_year:
#            raise forms.ValidationError('Year must be in the range %s - %s.' % (str(curr_year).zfill(2), str(max_year).zfill(2),))
#
#        return value

## An example Form based on ModelForm.
#class PaymentForm(forms.ModelForm):
#    cc_number = creditcards.CreditCardNumberField(required=False)
#    cc_expiry = creditcards.CreditCardExpiryField()
#
#    class Meta:
#        model = Payment
#
#    """
#        This function checks that the card number matches the card type.
#        If you don't want to do this, comment out this function.
#    """
#    def clean(self):
#        if self.cleaned_data:
#            if len(self.cleaned_data.items()) == len(self.fields):
#                if self.cleaned_data['method'] == 'cc':
#                    the_type = self.cleaned_data.get('cc_type', '')
#                    number = self.cleaned_data.get('cc_number', '')
#                    if not ValidateDigits(the_type, number):
#                        raise forms.ValidationError('Card Number is not a valid ' + the_type.upper() + ' card number.')
#                    if not self.instance.is_payment_valid():
#                        raise forms.ValidationError('Credit card payment could not be processed.  Reason is %s.  Check that card details are correct and try again.  If you still receive this error, check with your financial institution.' % (self.instance.gateway_resptxt))
#        return self.cleaned_data
