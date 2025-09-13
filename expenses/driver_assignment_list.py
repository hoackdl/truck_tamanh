from django.shortcuts import render, redirect
from .models import DriverAssignment
from .forms import DriverAssignmentForm
from django.db.models import Q
from datetime import date
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def driver_assignment_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    form = DriverAssignmentForm(request.POST or None)
    error_message = None

    if request.method == "POST" and form.is_valid():
        new_assignment = form.save(commit=False)
        new_assignment.user = request.user  # ✅ Gán user tạo

        # ❗ Tự động kết thúc gán cũ (cùng lái xe)
        old_assignments = DriverAssignment.objects.filter(
            driver=new_assignment.driver,
            end_date__isnull=True
        ).exclude(pk=new_assignment.pk)

        for old in old_assignments:
            old.end_date = new_assignment.start_date
            old.save()

        new_assignment.save()
        return redirect('driver_assignment_list')

    today = date.today()
    assignments = DriverAssignment.objects.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True)
    ).order_by('-start_date')

    context = {
        'form': form,
        'assignments': assignments,
    }
    return render(request, 'expenses/driver_assignment_list.html', context)


from django.shortcuts import get_object_or_404
from django.contrib import messages

@login_required
def driver_assignment_edit(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    assignment = get_object_or_404(DriverAssignment, pk=pk)
    form = DriverAssignmentForm(request.POST or None, instance=assignment)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật gán lái xe thành công.")
        return redirect('driver_assignment_list')

    context = {
        'form': form,
        'assignment': assignment,
    }
    return render(request, 'expenses/driver_assignment_edit.html', context)


@login_required
def driver_assignment_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    assignment = get_object_or_404(DriverAssignment, pk=pk)

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Xoá gán lái xe thành công.")
        return redirect('driver_assignment_list')

    context = {
        'assignment': assignment,
    }
    return render(request, 'expenses/driver_assignment_confirm_delete.html', context)
