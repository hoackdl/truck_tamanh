import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from .models import ExpenseEntry, ReceiptImage, DriverAssignment, Vehicle

def expense_export_excel(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    qs = ExpenseEntry.objects.all()

    if from_date:
        qs = qs.filter(date__gte=from_date)
    if to_date:
        qs = qs.filter(date__lte=to_date)

    # Tạo DataFrame từ queryset
    data = []
    for e in qs:
        data.append({
            'Thực hiện': e.get_payer_type_display(),
            'Biển số': e.vehicle.license_plate if e.vehicle else '',
            'Ngày': e.date.strftime("%d/%m/%Y"),
            'Người tạo': e.user.username,
            'Điểm nhận': e.pickup_location,
            'Điểm giao': e.delivery_location,
            'Có phiếu': e.with_receipt_amount,
            'Không phiếu': e.without_receipt_amount,
            'Ứng/Thu khách': e.advance_or_customer_payment,
            'Phụ cấp': e.allowance,
            'KM trên xe': e.km_on_vehicle,
            'Ghi chú': e.notes,
        })

    df = pd.DataFrame(data)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses')
        writer.close()  # Thay vì writer.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=expenses.xlsx'
    return response
