from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


# Расширенная модель пользователя
class User(AbstractUser):
    """
    Extended Django user model for authentication and user management.

    Attributes:
        email (EmailField): Unique email address used for authentication.
        phone_number (CharField): Optional phone number of the user.
        date_of_birth (DateField): Optional birth date of the user.
        address (TextField): Optional address information.
        created_at (DateTimeField): Timestamp when the user was created.
        updated_at (DateTimeField): Timestamp when the user was last updated.
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Only username required for createsuperuser

    def __str__(self):
        """
        Returns the string representation of the user.

        Returns:
            str: User's email address.
        """
        return self.email


class Product(models.Model):
    """
    Represents a product available for purchase.

    Attributes:
        name (CharField): Human readable product name.
        description (TextField): Detailed description of the product.
        price (DecimalField): Unit price with two decimal places.
        stock (IntegerField): Available stock quantity.
        category (CharField): Product category from predefined choices.
        image (ImageField): Image file uploaded to the 'products/' directory.
    """
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('home', 'Home & Garden'),
        ('sports', 'Sports'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        """
        Returns the string representation of the product.

        Returns:
            str: Product name.
        """
        return self.name


class Order(models.Model):
    """
    Represents a customer order consisting of multiple order items.

    Attributes:
        user (ForeignKey): Owner of the order.
        products (ManyToManyField): Products in the order through OrderItem.
        total_price (DecimalField): Cached total price of all items.
        status (CharField): Current status of the order.
        created_at (DateTimeField): Timestamp when the order was created.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the string representation of the order.

        Returns:
            str: Order ID and username.
        """
        return f"Order {self.id} by {self.user.username}"

    def calculate_total_price(self):
        """
        Calculates the total price of the order based on all order items.

        Returns:
            Decimal: The total price of all items in the order.
        """
        total = sum(
            item.quantity * item.price_at_purchase for item in self.items.all()
        )
        return total

    def save(self, *args, **kwargs):
        """
        Overrides save method to automatically update total_price before saving.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Сначала сохраняем объект, чтобы получить primary key
        if not self.pk:
            super().save(*args, **kwargs)

        # Затем обновляем total_price только если объект уже существует
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Represents a single line item within an order.

    Attributes:
        order (ForeignKey): Parent order this item belongs to.
        product (ForeignKey): The product being purchased.
        quantity (PositiveIntegerField): Quantity of the product ordered.
        price_at_purchase (DecimalField): Unit price captured at purchase time.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """
        Returns the string representation of the order item.

        Returns:
            str: Quantity and product name.
        """
        return f"{self.quantity} of {self.product.name}"

# Models User, Product, and Order have created_at and updated_at fields for tracking creation and update times.

# Основная логика работы:
# Пользователь создает заказ
# Товары добавляются в заказ через OrderItem с фиксацией текущей цены
# При сохранении заказа автоматически пересчитывается общая стоимость
# Статус заказа отслеживается от "pending" до "delivered"
# Эта архитектура обеспечивает целостность данных и правильное ценообразование в электронной коммерции.