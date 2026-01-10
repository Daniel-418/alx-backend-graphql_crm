# type: ignore
from django.db import models
from django.utils import timezone


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)


class Order(models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    products = models.ManyToManyField(Product)
    order_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(f"Order: ${self.id}")
