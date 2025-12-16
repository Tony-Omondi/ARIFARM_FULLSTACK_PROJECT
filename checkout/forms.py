# checkout/forms.py
from django import forms

ZONES = [
    ('', 'Select Delivery Zone'),
    ('Westlands', 'Westlands'),
    ('Kilimani', 'Kilimani'),
    ('Ngong Road', 'Ngong Road'),
    ('CBD', 'CBD'),
    ('Lavington', 'Lavington'),
    ('Karen', 'Karen'),
    ('Other', 'Other'),
]

class CheckoutForm(forms.Form):
    email = forms.EmailField(label="Email Address", required=True)
    phone_number = forms.CharField(
        label="Phone Number (07xx or 2547xx)",
        max_length=15,
        help_text="Used for M-Pesa payment"
    )
    zone = forms.ChoiceField(choices=ZONES, label="Delivery Zone")