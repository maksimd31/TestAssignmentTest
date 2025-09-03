from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product, Order, OrderItem

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for User model"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'date_of_birth': date(1990, 1, 1),
            'address': 'Test Address 123'
        }

    def test_create_user_success(self):
        """Test successful user creation"""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.phone_number, self.user_data['phone_number'])
        self.assertEqual(user.date_of_birth, self.user_data['date_of_birth'])
        self.assertEqual(user.address, self.user_data['address'])
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])

    def test_email_uniqueness(self):
        """Test email uniqueness constraint"""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser2',
                email=self.user_data['email'],
                password='testpass123'
            )

    def test_user_with_minimal_data(self):
        """Test user creation with minimal required data"""
        user = User.objects.create_user(
            username='minimaluser',
            email='minimal@example.com',
            password='testpass123'
        )

        self.assertEqual(user.email, 'minimal@example.com')
        self.assertEqual(user.phone_number, None)
        self.assertEqual(user.date_of_birth, None)
        self.assertEqual(user.address, None)


class ProductModelTest(TestCase):
    """Tests for Product model"""

    def setUp(self):
        """Set up test data"""
        self.product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': Decimal('99.99'),
            'stock': 10,
            'category': 'electronics'
        }

    def test_create_product_success(self):
        """Test successful product creation"""
        product = Product.objects.create(**self.product_data)

        self.assertEqual(product.name, self.product_data['name'])
        self.assertEqual(product.description, self.product_data['description'])
        self.assertEqual(product.price, self.product_data['price'])
        self.assertEqual(product.stock, self.product_data['stock'])
        self.assertEqual(product.category, self.product_data['category'])

    def test_product_str_representation(self):
        """Test product string representation"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(str(product), self.product_data['name'])

    def test_product_category_choices(self):
        """Test valid product category choices"""
        valid_categories = ['electronics', 'clothing', 'books', 'home', 'sports']

        for category in valid_categories:
            product_data = self.product_data.copy()
            product_data['category'] = category
            product = Product.objects.create(**product_data)
            self.assertEqual(product.category, category)

    def test_product_default_stock(self):
        """Test default stock value"""
        product_data = self.product_data.copy()
        del product_data['stock']
        product = Product.objects.create(**product_data)
        self.assertEqual(product.stock, 0)


class OrderModelTest(TestCase):
    """Tests for Order model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product1 = Product.objects.create(
            name='Product 1',
            description='Description 1',
            price=Decimal('10.00'),
            stock=100,
            category='electronics'
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            description='Description 2',
            price=Decimal('20.00'),
            stock=50,
            category='books'
        )

    def test_create_order_success(self):
        """Test successful order creation"""
        order = Order(user=self.user)
        order.save()

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_price, Decimal('0'))
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.id)

    def test_order_str_representation(self):
        """Test order string representation"""
        order = Order(user=self.user)
        order.save()
        expected_str = f"Order {order.id} by {self.user.username}"
        self.assertEqual(str(order), expected_str)

    def test_order_status_choices(self):
        """Test valid order status choices"""
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

        for status_value in valid_statuses:
            order = Order(user=self.user, status=status_value)
            order.save()
            self.assertEqual(order.status, status_value)

    def test_calculate_total_price_empty_order(self):
        """Test total price calculation for empty order"""
        order = Order(user=self.user)
        order.save()
        total = order.calculate_total_price()
        self.assertEqual(total, 0)

    def test_calculate_total_price_with_items(self):
        """Test total price calculation for order with items"""
        order = Order(user=self.user)
        order.save()

        # Create items in the order
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price_at_purchase=self.product1.price
        )
        OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            price_at_purchase=self.product2.price
        )

        expected_total = (2 * Decimal('10.00')) + (1 * Decimal('20.00'))
        calculated_total = order.calculate_total_price()
        self.assertEqual(calculated_total, expected_total)


class OrderItemModelTest(TestCase):
    """Tests for OrderItem model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('15.50'),
            stock=100,
            category='electronics'
        )
        self.order = Order(user=self.user)
        self.order.save()

    def test_create_order_item_success(self):
        """Test successful order item creation"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_purchase=self.product.price
        )

        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.price_at_purchase, self.product.price)

    def test_order_item_str_representation(self):
        """Test order item string representation"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_purchase=self.product.price
        )
        expected_str = f"2 of {self.product.name}"
        self.assertEqual(str(order_item), expected_str)

    def test_order_item_default_quantity(self):
        """Test default quantity value"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price_at_purchase=self.product.price
        )
        self.assertEqual(order_item.quantity, 1)


class RegisterAPIViewTest(APITestCase):
    """Tests for user registration API"""

    def setUp(self):
        """Set up test data"""
        self.register_url = reverse('shop:register')
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.valid_user_data['email'])

        # Check that user was created in database
        self.assertTrue(User.objects.filter(email=self.valid_user_data['email']).exists())

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create existing user
        User.objects.create_user(
            username='existing_user',
            email=self.valid_user_data['email'],
            password='testpass123'
        )

        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that response contains email validation error
        self.assertIn('email', response.data)

    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        invalid_data = {
            'username': '',
            'email': 'invalid_email',
            'password': '123',  # Too short password
        }

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPIViewTest(APITestCase):
    """Tests for user authentication API"""

    def setUp(self):
        """Set up test data"""
        self.login_url = reverse('shop:login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_success(self):
        """Test successful user authentication"""
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)

        # Check user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['username'], self.user.username)

    def test_login_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        invalid_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test authentication of non-existent user"""
        nonexistent_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, nonexistent_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_data(self):
        """Test authentication with missing data"""
        incomplete_data = {
            'email': 'test@example.com'
            # Missing password
        }

        response = self.client.post(self.login_url, incomplete_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IntegrationTest(TestCase):
    """Integration tests for related models"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('25.99'),
            stock=100,
            category='electronics'
        )

    def test_complete_order_workflow(self):
        """Test complete order creation and processing workflow"""
        # Create order
        order = Order(user=self.user)
        order.save()
        self.assertEqual(order.status, 'pending')

        # Add item to order
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price_at_purchase=self.product.price
        )

        # Check relationships
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first(), order_item)
        self.assertEqual(self.product.order_items.count(), 1)

        # Check total price calculation
        expected_total = 2 * Decimal('25.99')
        calculated_total = order.calculate_total_price()
        self.assertEqual(calculated_total, expected_total)

        # Update order status
        order.status = 'processing'
        order.save()
        self.assertEqual(order.status, 'processing')

    def test_user_orders_relationship(self):
        """Test user orders relationship"""
        # Create multiple orders for user
        order1 = Order(user=self.user)
        order1.save()
        order2 = Order(user=self.user, status='processing')
        order2.save()

        # Check relationship
        user_orders = self.user.orders.all()
        self.assertEqual(user_orders.count(), 2)
        self.assertIn(order1, user_orders)
        self.assertIn(order2, user_orders)

    def test_product_in_multiple_orders(self):
        """Test product in multiple orders"""
        # Create two orders
        order1 = Order(user=self.user)
        order1.save()
        order2 = Order(user=self.user)
        order2.save()

        # Add same product to both orders
        OrderItem.objects.create(
            order=order1,
            product=self.product,
            quantity=1,
            price_at_purchase=self.product.price
        )
        OrderItem.objects.create(
            order=order2,
            product=self.product,
            quantity=3,
            price_at_purchase=self.product.price
        )

        # Check relationships
        self.assertEqual(self.product.order_items.count(), 2)
        self.assertEqual(order1.products.count(), 1)
        self.assertEqual(order2.products.count(), 1)
