from django import forms
from .models import ExpenseEntry
from django.forms import DateInput, TextInput, Select, Textarea

class ExpenseEntryForm(forms.ModelForm):
    class Meta:
        model = ExpenseEntry
        exclude = ['user']  # 👈 Quan trọng: không hiển thị trường này
       

        widgets = {
            'date': DateInput(
                format='%d/%m/%y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # dùng type text để cho phép định dạng custom
                    'placeholder': 'dd/mm/yy'
                }
            ),
            'payer_type': Select(attrs={'class': 'form-control'}),
            'pickup_location': TextInput(attrs={'class': 'form-control'}),
            'delivery_location': TextInput(attrs={'class': 'form-control'}),
            'with_receipt_amount': TextInput(attrs={'class': 'form-control price-format'}),
            'without_receipt_amount': TextInput(attrs={'class': 'form-control price-format'}),
            'allowance': TextInput(attrs={'class': 'form-control price-format'}),
            'cost_type': Select(attrs={'class': 'form-select'}),
            'km_on_vehicle': TextInput(attrs={'class': 'form-control price-format'}),
            'advance_or_customer_payment': TextInput(attrs={'class': 'form-control price-format'}),
            'notes': Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%d/%m/%y']
