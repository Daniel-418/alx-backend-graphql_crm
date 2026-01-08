from django.db import models


# Create your models here.
class Customer(models.Model):
    name = models.CharField()
    email = models.EmailField()
    phone = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)
