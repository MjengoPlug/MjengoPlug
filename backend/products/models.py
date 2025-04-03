from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)


    def __str__(self):
        return self.name


class Product(models.Model):
    business = models.ForeignKey('accounts.Business', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)


    # class Meta:
    #     constraints=[
    #         models.UniqueConstraint(fields=['business', 'name'], name='unique_product_business'),
    #         models.CheckConstraint(check=models.Q(price__gte=0), name='price_gte_0'),
           
    #     ]

    def clean(self):
        if self.price < 0:
            raise ValueError('Price must be greater than 0')
        
        if self.stock < 0:
            raise ValueError('Stock must be greater than 0')
           
    def __str__(self):
        return self.name
    
    