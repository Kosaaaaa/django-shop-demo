from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
# from cart.models import Coupon
User = get_user_model()


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(blank=True, null=True, max_length=16)
    # used_coupons = models.ManyToManyField(
    #     Coupon, related_name='user_used_coupons', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


def post_save_user_receiver(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance, first_name=instance.first_name,
                                last_name=instance.last_name, email=instance.email)


post_save.connect(post_save_user_receiver, sender=User)
