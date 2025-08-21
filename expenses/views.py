


from django.http import HttpResponse

from django.shortcuts import render
from .models import ExpenseEntry, ReceiptImage  # model bạn dùng
from django.contrib.auth.decorators import login_required
# expenses/views.py
from django.shortcuts import render, redirect
from .forms import ExpenseEntryForm
from django.db.models.functions import Coalesce
from django.db.models import Sum, Value, DecimalField


from django.contrib.auth.decorators import login_required
from .models import ExpenseEntry

@login_required
def expense_list(request):
    if request.user.is_superuser:
        entries = ExpenseEntry.objects.all().order_by('-date')  # Admin: xem tất cả
    else:
        entries = ExpenseEntry.objects.filter(user=request.user).order_by('-date')  # User thường: chỉ xem của mình
    return render(request, 'expenses/expense_list.html', {'entries': entries})





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ExpenseEntryForm


@login_required
def expense_entry_create(request):
    if request.method == "POST":
        form = ExpenseEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()

            for img in request.FILES.getlist('receipt_images'):
                ReceiptImage.objects.create(expense=entry, image=img)

            return redirect("expense_list")
    else:
        form = ExpenseEntryForm()
    return render(request, "expenses/expense_form.html", {"form": form})





from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ExpenseEntry

@login_required
def expense_delete(request, pk):
    entry = get_object_or_404(ExpenseEntry, pk=pk)

    # (Tuỳ chọn) kiểm tra quyền:
    if request.user != entry.user and not request.user.is_superuser:
        return redirect('expense_list')  # Hoặc trả về 403

    entry.delete()
    return redirect('expense_list')  # Đổi theo tên trang danh sách


from django.shortcuts import render, get_object_or_404, redirect
from .models import ExpenseEntry
from .forms import ExpenseEntryForm

from .models import ExpenseEntry, ReceiptImage

def expense_edit(request, pk):
    entry = get_object_or_404(ExpenseEntry, pk=pk)

    if request.method == 'POST':
        form = ExpenseEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()

            # ✅ Nếu có thêm ảnh mới → lưu tiếp
            for img in request.FILES.getlist('receipt_images'):
                ReceiptImage.objects.create(expense=entry, image=img)

            return redirect('expense_list')
    else:
        form = ExpenseEntryForm(instance=entry)

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'entry': entry  # ✅ Truyền entry vào để hiển thị ảnh cũ
    })



from datetime import datetime, date
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render
from .models import ExpenseEntry


def expense_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    today = date.today()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else today
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else today

    entries = ExpenseEntry.objects.filter(
        date__range=(start_date, end_date),
        payer_type='driver'
    )

    if not request.user.is_staff:
        entries = entries.filter(user=request.user)

    if request.user.is_staff:
        # Tổng từng người
        user_totals = (
            entries
            .values('user__username')
            .annotate(
                total_with=Sum('with_receipt_amount'),
                total_without=Sum('without_receipt_amount'),
                total_allowance=Sum('allowance'),
                total_advance=Sum('advance_or_customer_payment'),
            )
            .order_by('user__username')
        )

        totals_by_user = []
        for row in user_totals:
            row['remaining'] = (
                (row['total_advance'] or 0)
                - (row['total_with'] or 0)
                - (row['total_without'] or 0)
                - (row['total_allowance'] or 0)
            )
            totals_by_user.append(row)

    else:
        # Nếu là lái xe
        sums = entries.aggregate(
            total_with=Coalesce(Sum('with_receipt_amount', output_field=DecimalField()), Value(0, output_field=DecimalField())),
            total_without=Coalesce(Sum('without_receipt_amount', output_field=DecimalField()), Value(0, output_field=DecimalField())),
            total_allowance=Coalesce(Sum('allowance', output_field=DecimalField()), Value(0, output_field=DecimalField())),
            total_advance=Coalesce(Sum('advance_or_customer_payment', output_field=DecimalField()), Value(0, output_field=DecimalField())),
        )

        remaining = (
            sums['total_advance']
            - sums['total_with']
            - sums['total_without']
            - sums['total_allowance']
        )

        totals_by_user = [{
            'user__username': request.user.username,
            'total_with': sums['total_with'],
            'total_without': sums['total_without'],
            'total_allowance': sums['total_allowance'],
            'total_advance': sums['total_advance'],
            'remaining': remaining,
        }]

    # Tổng toàn bộ cho cả admin và tài xế
    totals = entries.aggregate(
        total_with=Coalesce(Sum('with_receipt_amount', output_field=DecimalField()), Value(0, output_field=DecimalField())),
        total_without=Coalesce(Sum('without_receipt_amount', output_field=DecimalField()), Value(0, output_field=DecimalField())),
        total_allowance=Coalesce(Sum('allowance', output_field=DecimalField()), Value(0, output_field=DecimalField())),
        total_advance=Coalesce(Sum('advance_or_customer_payment', output_field=DecimalField()), Value(0, output_field=DecimalField())),
    )

    remaining_balance = (
        totals['total_advance']
        - totals['total_with']
        - totals['total_without']
        # - totals['total_allowance']  # nếu không tính allowance vào trừ
    )

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'totals_by_user': totals_by_user,
        'totals': totals,
        'remaining_balance': remaining_balance,
        'is_admin': request.user.is_staff,
    }

    return render(request, 'expenses/expense_report.html', context)

def create_expense(request):
    if request.method == 'POST':
        form = ExpenseEntryForm(request.POST, request.FILES)  # <== thêm request.FILES
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseEntryForm()
    return render(request, 'expense_form.html', {'form': form})
