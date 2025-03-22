from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)


    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

 


    def __str__(self):
        return self.name
    