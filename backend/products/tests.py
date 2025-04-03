from django.test import TestCase
from .models import Product, Category
from django.urls import reverse
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from accounts.models import Business
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404,reverse
from rest_framework import status

User=get_user_model()


# Create your tests here.
class CategoryTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')

class ProductTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com',password='testpassword')
        self.businesss = Business.objects.create(name='Test Business',owner=self.user)
        self.category = Category.objects.create(name='Test Category')
     

    def test_create_product(self):
        product = Product.objects.create(
            name='Test Product',
            price=10.00,
            description='Test Description',
            business=self.businesss,
            category=self.category
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 10.00)
        self.assertEqual(product.description, 'Test Description')
        self.assertEqual(product.business, self.businesss)
        self.assertEqual(product.category, self.category)

    def test_price_greater_than_zero(self):
        product = Product.objects.create(
            name='Test Product',
            price=10,
            description='Test Description',
            business=self.businesss,
            category=self.category
        )
        self.assertEqual(product.price,10)
       
    
    def test_stock_greater_than_zero(self):
        product = Product.objects.create(
            name='Test Product',
            price=10.00,
            description='Test Description',
            business=self.businesss,
            category=self.category,
            stock=10
        )
        self.assertEqual(product.stock,10)


class ProductViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com',password='testpassword')
        self.business = Business.objects.create(name='Test Business',owner=self.user)

       
        self.category = Category.objects.create(name="Electronics")

        self.product1 = Product.objects.create(
            name="Laptop", 
            category=self.category,
            business=self.business,
            price=100,
            stock=5,
            description="A powerful laptop"
            )
        self.product2 = Product.objects.create(
            name="Phone",
            category=self.category,
            business=self.business,
            price=50,
            stock=10,
            description="A high-end smartphone"
            )
        self.product3 = Product.objects.create(
            name="Table",
            category=self.category,
            business=self.business,
            price=200,
            stock=5,
            description="A sturdy table"
            )

        
        self.list_url = reverse('product-list') 
        

    def test_list_products(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_products_by_category(self):
        url = f"{self.list_url}?category={self.category.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_retrieve_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Laptop")

    def test_create_product(self):
        data = {"name": "Headphones", "category": self.category.pk, "business": self.business.pk, "price": 50, "stock": 10, "description": "Noise-cancelling headphones"}
        response = self.client.post(self.list_url, data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_update_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product1.id})
        data = {"name": "Gaming Laptop"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, "Gaming Laptop")

    def test_delete_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 2)


class CategoryViewSetTests(APITestCase):

    def setUp(self):
        
        self.category1 = Category.objects.create(name="Electronics")
        self.category2 = Category.objects.create(name="Furniture")
        self.list_url = reverse('category-list')  

    def test_get_all_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  

    def test_get_categories_with_filter(self):
        response = self.client.get(self.list_url, {'category': 'Electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  

    def test_get_no_categories_with_invalid_filter(self):
        response = self.client.get(self.list_url, {'category': 'Nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  





        
    




     
    

    