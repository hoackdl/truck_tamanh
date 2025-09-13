

from .models import ExpenseEntry, ReceiptImage, DriverAssignment, Vehicle
from .forms import ExpenseEntryForm
from datetime import date
from django.db.models import Q


from datetime import date
from django.db.models import Q
from .models import DriverAssignment
from django.http import HttpResponseForbidden

from django.shortcuts import render
from .models import Driver, DriverAssignment, ExpenseEntry, ReceiptImage
from django.contrib.auth.decorators import login_required
# expenses/views.py
from django.shortcuts import render, redirect
from .forms import ExpenseEntryForm
from django.db.models.functions import Coalesce
from django.db.models import Sum, Value, DecimalField

from django.utils import timezone  # ✅ Đúng
from django.contrib.auth.decorators import login_required
from .models import ExpenseEntry

from .models import ExpenseEntry, DriverAssignment
from datetime import date

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def expense_list(request):
    if request.method == "POST":
        ids_to_delete = request.POST.getlist("selected_ids")
        ExpenseEntry.objects.filter(id__in=ids_to_delete).delete()

    if request.user.is_superuser:
        entries = ExpenseEntry.objects.all().order_by('-date')
    else:
        entries = ExpenseEntry.objects.filter(user=request.user).order_by('-date')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        entries = entries.filter(date__gte=from_date)
    if to_date:
        entries = entries.filter(date__lte=to_date)

    # Gán xe tự động nếu chưa có
    for entry in entries:
        if not entry.vehicle and entry.driver:
            assignment = DriverAssignment.objects.filter(
                driver=entry.driver,
                start_date__lte=entry.date
            ).filter(
                Q(end_date__gte=entry.date) | Q(end_date__isnull=True)
            ).order_by('-start_date').first()
            if assignment:
                entry.vehicle = assignment.vehicle
                entry.save()

    paginator = Paginator(entries, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'expenses/expense_list.html', {
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
    })




@login_required
def expense_entry_create(request):
    driver = getattr(request.user, 'driver', None)

    if request.method == "POST":
        form = ExpenseEntryForm(request.POST, request.FILES, driver=driver.id if driver else None)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user

            if driver:
                entry.driver = driver

            # Tự động gán vehicle nếu chưa chọn
            if not form.cleaned_data.get('vehicle'):
                today = entry.date or timezone.now().date()
                assignment = DriverAssignment.objects.filter(
                    driver=entry.driver,
                    start_date__lte=today
                ).filter(
                    Q(end_date__gte=today) | Q(end_date__isnull=True)
                ).order_by('-start_date').first()

                if assignment:
                    entry.vehicle = assignment.vehicle
                else:
                    print("Không tìm thấy DriverAssignment phù hợp cho driver và ngày.")
                    print("Driver:", entry.driver)
                    print("Ngày:", today)
                    print("Tất cả assignment của driver:", list(DriverAssignment.objects.filter(driver=entry.driver)))
            else:
                entry.vehicle = form.cleaned_data['vehicle']

            entry.save()

            for img in request.FILES.getlist('receipt_images'):
                ReceiptImage.objects.create(expense=entry, image=img)

            return redirect("expense_list")
        else:
            print("Form errors:", form.errors)
    else:
        form = ExpenseEntryForm(driver=driver.id if driver else None)

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
from django.contrib.auth.models import User

def expense_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    selected_user_id = request.GET.get('user')

    today = date.today()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else today
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else today

    # 👇 Lấy tất cả chi phí (dù của công ty hay tài xế)
    all_entries = ExpenseEntry.objects.filter(
        date__range=(start_date, end_date)
    )

    # 👇 Chỉ lấy chi phí do tài xế chi để tính tồn
    entries = all_entries.filter(payer_type='driver')

    if not request.user.is_staff:
        entries = entries.filter(user=request.user)

    if request.user.is_staff and selected_user_id:
        entries = entries.filter(user__id=selected_user_id)

    if request.user.is_staff:
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

    if request.user.is_staff and selected_user_id:
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
            - totals['total_allowance']
        )
    else:
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
            - totals['total_allowance']
        )

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'totals_by_user': totals_by_user,
        'totals': totals,
        'remaining_balance': remaining_balance,
        'is_admin': request.user.is_staff,
        'users': User.objects.all() if request.user.is_staff else None,
        'selected_user_id': int(selected_user_id) if selected_user_id else None,
    }

    return render(request, 'expenses/expense_report.html', context)
