from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Customer_details(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Bill(models.Model):
    customer = models.ForeignKey(Customer_details, on_delete=models.CASCADE, null=True, blank=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    subtotal = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    cgst = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
    gst = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # Auto generate invoice number if not set
        if not self.invoice_number:
            last_bill = Bill.objects.exclude(invoice_number__isnull=True).exclude(invoice_number="").order_by("-id").first()
            if last_bill and last_bill.invoice_number and last_bill.invoice_number.startswith("BILL"):
                try:
                    last_num = int(last_bill.invoice_number.replace("BILL", ""))
                    self.invoice_number = f"BILL{last_num+1:04d}"
                except ValueError:
                    self.invoice_number = "BILL0001"
            else:
                self.invoice_number = "BILL0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name if self.customer else 'No Customer'}"


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField()

    def __str__(self):
        return f"{self.item_name} ({self.quantity} × {self.price})"
