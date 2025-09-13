from django import forms
from .models import ExpenseEntry, Driver, Vehicle, DriverAssignment
from django.forms import DateInput, TextInput, Select, Textarea


# forms.py
from django import forms
from .models import ExpenseEntry, Driver
from django.forms import DateInput, Select, TextInput, Textarea

class ExpenseEntryForm(forms.ModelForm):
    class Meta:
        model = ExpenseEntry
        exclude = ['user', 'vehicle']  # vehicle sẽ gán trong view
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'driver': Select(attrs={'class': 'form-select'}),
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
        driver_id = kwargs.pop('driver', None)
        super().__init__(*args, **kwargs)

        self.fields['date'].input_formats = ['%Y-%m-%d']

        if driver_id:
            self.fields['driver'].queryset = Driver.objects.filter(id=driver_id)
            self.fields['driver'].initial = driver_id
            self.fields['driver'].widget = forms.HiddenInput()



# forms.py
from .models import DriverAssignment
from django import forms

class DriverAssignmentForm(forms.ModelForm):
    class Meta:
        model = DriverAssignment
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên lái xe'})
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'license_plate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên phương tiện'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Biển số'})
                    }