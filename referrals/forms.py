from django import forms
from referrals.models import ReferralCode
from referrals.utils import apply_referral_logic

class ReferralSignupForm(forms.Form):
    referral_code = forms.CharField(
        max_length=20, 
        required=False,
        label='Referral Code (Optional)',
        widget=forms.TextInput(attrs={'placeholder': 'Enter referral code'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check for 'ref' in initial or data if not provided
        if 'initial' in kwargs and 'ref' in kwargs['initial']:
            self.fields['referral_code'].initial = kwargs['initial']['ref']

    def clean_referral_code(self):
        code = self.cleaned_data.get('referral_code')
        if code:
            if not ReferralCode.objects.filter(code=code, is_active=True).exists():
                raise forms.ValidationError("Invalid referral code. Please check and try again.")
        return code

    def signup(self, request, user):
        code = self.cleaned_data.get('referral_code')
        if code:
            apply_referral_logic(user, code)
