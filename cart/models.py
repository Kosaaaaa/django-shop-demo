from core.models import Customer
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from pipenv.vendor.backports.enum import unique

User = get_user_model()
DEFAULT_SHIPPING_ID = 1


class Coupon(models.Model):
    name = models.CharField(max_length=15)
    code = models.CharField(max_length=15, unique=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=False)

    percent = models.IntegerField(validators=(
        MinValueValidator(0), MaxValueValidator(100)))

    @property
    def multiplier(self):
        """
            Get mulitplier from percent
            15% -> 0.15
        """
        return self.percent / 100

    def __str__(self):
        return f'{self.name} - {self.code}'


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True)
    slug = models.SlugField(
        max_length=150, unique=True, blank=True)

    class Meta:
        # ordering = ('name',)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Address(models.Model):
    ADDRESS_CHOICES = (
        ('B', 'Billing'),
        ('S', 'Shipping'),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(blank=True, null=True, max_length=12)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        if self.address_line_2 is None or self.address_line_2 == '':
            return f"{self.address_line_1}, {self.city}, {self.zip_code}"
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.zip_code}"

    class Meta:
        verbose_name_plural = 'Addresses'


class Size(models.Model):
    name = models.CharField(max_length=8, unique=True)
    size_order = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ('size_order',)

    def __str__(self):
        return self.name


class SizeVariations(models.Model):
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, null=True)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Size Variations'
        unique_together = (
            ('size', 'product'),
        )
        ordering = ('product', 'size__size_order')

    def __str__(self):
        # return f'{self.product.title} - {self.size.name}'
        return self.size.name


class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, blank=True, unique=True)

    image = models.ImageField(blank=True, null=True,
                              upload_to='product_images/%Y/%m/%d/')
    image_2 = models.ImageField(
        blank=True, null=True, upload_to='product_images/%Y/%m/%d/')
    image_3 = models.ImageField(
        blank=True, null=True, upload_to='product_images/%Y/%m/%d/')
    image_4 = models.ImageField(
        blank=True, null=True, upload_to='product_images/%Y/%m/%d/')

    description = models.TextField()
    price = models.IntegerField(
        default=0, help_text="Please type price in integer eq. 12.50 PLN -> 1250 PLN")
    sale = models.BooleanField(default=False)
    sale_price = models.IntegerField(
        blank=True, null=True, help_text="Please type price in integer eq. 12.50 PLN -> 1250 PLN")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    primary_category = models.ForeignKey(
        Category, related_name='primary_products', blank=True, null=True, on_delete=models.CASCADE)
    secondary_categories = models.ManyToManyField(Category, blank=True)

    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    class Meta:
        ordering = ('title',)
        # index_together = (('id', 'slug'),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cart:product-detail", kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse("staff:product-update", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("staff:product-delete", kwargs={'pk': self.pk})

    def get_price(self):
        return "{:.2f}".format(self.price / 100)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except ValueError:
            url = ''
        return url

    @property
    def image_alt_text(self):
        return f'{self.title} {self.primary_category}'

    @property
    def stock(self):
        stock = SizeVariations.objects.filter(
            product__title=self.title).aggregate(models.Sum('stock'))
        stock_values = list(stock.values())
        if stock_values[0] is not None:
            return stock_values[0]
        else:
            return 0

    @property
    def available_sizes(self):
        # TODO test it
        sizes = SizeVariations.objects.filter(product__title=self.title)
        return sizes

    @property
    def in_stock(self):
        return self.stock > 0


class ShippingMethod(models.Model):
    provider = models.CharField(max_length=100, unique=True)
    price = models.PositiveSmallIntegerField(
        default=0, help_text="Please type price in integer eq. 12.50 PLN -> 1250 PLN")

    def __str__(self):
        return self.provider

    @property
    def price_formatted(self):
        return "{:.2f}".format(self.price / 100)


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(SizeVariations, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} - {self.size.size}"

    def get_raw_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_item_price(self):
        price = self.get_raw_total_item_price()  # 1000
        return "{:.2f}".format(price / 100)


class Order(models.Model):
    customer = models.ForeignKey(Customer, blank=True,
                                 null=True, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    paid = models.BooleanField(default=False)

    shipped = models.BooleanField(default=False)
    shipping_tracking = models.CharField(max_length=50, null=True, blank=True)
    shipping_method = models.ForeignKey(
        ShippingMethod, blank=True, null=True, on_delete=models.SET_NULL, default=DEFAULT_SHIPPING_ID)

    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')

    billing_address = models.ForeignKey(
        Address, related_name='billing_address', blank=True, null=True, on_delete=models.SET_NULL)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_address', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        # ordering = ('ordered', '-ordered_date')
        ordering = ('-start_date',)

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"O-{self.pk}"

    def get_raw_subtotal(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()
        return total

    @property
    def subtotal_formatted(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(subtotal / 100)

    def get_coupon_discount(self):
        discount = self.get_raw_subtotal() * self.coupon.multiplier
        return discount

    def get_raw_subtotal_discount(self):
        subtotal = self.get_raw_subtotal()
        if self.coupon is not None:
            subtotal -= self.get_coupon_discount()
        return subtotal

    def get_subtotal(self):
        subtotal = self.get_raw_subtotal_discount()
        return "{:.2f}".format(subtotal / 100)

    def get_raw_total(self):
        subtotal = self.get_raw_subtotal_discount()
        # add delivery
        subtotal += self.shipping_method.price
        # total = subtotal + delivery
        return subtotal

    def get_total(self):
        total = self.get_raw_total()
        return "{:.2f}".format(total / 100)


class Payment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=(
        ('PayPal', 'PayPal'),
    ))
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    amount = models.FloatField()
    raw_response = models.TextField()

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"PAYMENT-{self.order}-{self.pk}"


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(instance.title)

        has_slug = Product.objects.filter(slug=slug).exists()
        count = 1

        while has_slug:
            count += 1
            slug = slugify(instance.title) + '-' + str(count)
            has_slug = Product.objects.filter(slug=slug).exists()

        instance.slug = slug


pre_save.connect(pre_save_product_receiver, sender=Product)


def pre_save_category_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(instance.name)

        has_slug = Category.objects.filter(slug=slug).exists()
        count = 1

        while has_slug:
            count += 1
            slug = slugify(instance.name) + '-' + str(count)
            has_slug = Category.objects.filter(slug=slug).exists()

        instance.slug = slug


pre_save.connect(pre_save_category_receiver, sender=Category)


def pre_save_payment_receiver(sender, instance, *args, **kwargs):
    if instance.successful:
        order = instance.order
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            size_variation = SizeVariations.objects.get(id=item.size.id)
            size_variation.stock -= item.quantity
            size_variation.save()
        order.paid = True
        order.ordered = True
        order.save()


pre_save.connect(pre_save_payment_receiver, sender=Payment)
