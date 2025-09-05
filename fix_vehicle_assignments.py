from expenses.models import ExpenseEntry, DriverAssignment
from django.db.models import Q

def fix_entries():
    entries = ExpenseEntry.objects.filter(vehicle__isnull=True, driver__isnull=False)
    print(f"🔍 Có {entries.count()} entry cần cập nhật.")

    for entry in entries:
        assignment = DriverAssignment.objects.filter(
            driver=entry.driver,
            start_date__lte=entry.date
        ).filter(
            Q(end_date__gte=entry.date) | Q(end_date__isnull=True)
        ).order_by('-start_date').first()

        if assignment and assignment.vehicle:
            entry.vehicle = assignment.vehicle
            entry.save()
            print(f"✅ Đã gán xe {assignment.vehicle.license_plate} cho entry ID {entry.id}")
        elif assignment:
            print(f"⚠️ Gán lái xe tồn tại nhưng không có xe (entry ID {entry.id})")
        else:
            print(f"❌ Không tìm thấy gán xe phù hợp (entry ID {entry.id})")


from expenses.models import ExpenseEntry, DriverAssignment
from django.db.models import Q

for entry in ExpenseEntry.objects.filter(vehicle__isnull=True):
    print(f"Entry id={entry.id} driver={entry.driver} date={entry.date}")
    assignment = DriverAssignment.objects.filter(
        driver=entry.driver,
        start_date__lte=entry.date
    ).filter(
        Q(end_date__gte=entry.date) | Q(end_date__isnull=True)
    ).order_by('-start_date').first()
    
    if assignment:
        print(f"  Found assignment: vehicle={assignment.vehicle}")
    else:
        print("  No assignment found.")