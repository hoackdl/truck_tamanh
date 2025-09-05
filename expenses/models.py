from django.contrib.auth.models import User
from django.db import models



class Driver(models.Model):
    name = models.CharField("Tên lái xe", max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # 🔗 liên kết User

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    license_plate = models.CharField("Biển số", max_length=20)
    name = models.CharField("Tên xe", max_length=100, blank=True)

    def __str__(self):
        return f"{self.license_plate} - {self.name}"
    
class DriverAssignment(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField("Ngày bắt đầu áp dụng")
    end_date = models.DateField("Ngày kết thúc áp dụng", null=True, blank=True)

    class Meta:
        unique_together = ('driver', 'vehicle', 'start_date')  # Tránh trùng lịch

    def __str__(self):
        return f"{self.driver} -> {self.vehicle} ({self.start_date} - {self.end_date or 'hiện tại'})"

class ExpenseEntry(models.Model):
    payer_type = models.CharField(
        "Thực hiện",
        choices=[
            ('driver', 'Lái xe'),
            ('company', 'Công ty'),
        ],
        max_length=10,
        blank=True,
        default='driver'  # ✅ mặc định là 'driver'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField("Ngày")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_location = models.CharField("Điểm nhận hàng", max_length=100, blank=True)
    delivery_location = models.CharField("Điểm giao hàng", max_length=100, blank=True)

    with_receipt_amount = models.PositiveIntegerField("Có phiếu (VNĐ)", null=True, blank=True)
    without_receipt_amount = models.PositiveIntegerField("Không phiếu (VNĐ)", null=True, blank=True)
    
    cost_type = models.CharField("Loại chi phí", choices=[
        ('fuel', 'Nhiên liệu'),
        ('fuel', 'Làm hàng'),
        ('advance payment', 'Ứng'),
        ('payment', 'Thu khách'),
        ('meal', 'Xe nâng'),
        ('meal', 'Bốc xếp'),
        ('other', 'Khác'),
    ], max_length=20, blank=True)

    allowance = models.DecimalField(max_digits=12, decimal_places=0, default=0, null=True, blank=True)

    km_on_vehicle = models.IntegerField(default=0, blank=True)
    advance_or_customer_payment = models.DecimalField(max_digits=12, decimal_places=0,default=0, verbose_name="Thu khách / Ứng tiền")
    notes = models.TextField("Ghi chú", blank=True)

    def __str__(self):
        return f"{self.date} - {self.pickup_location} → {self.delivery_location}"


class ReceiptImage(models.Model):
    expense = models.ForeignKey(ExpenseEntry, on_delete=models.CASCADE, related_name='receipt_images')
    image = models.ImageField(upload_to='receipts/')


