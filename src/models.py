from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_not_empty(value):
    if value is None:
        raise ValidationError(_('This field cant be null.'))
    
    if isinstance(value, str) and value.strip() == '':
        raise ValidationError(_('This field cannot be empty.'))
    
    return value


class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def for_product(self, product_id):
        return self.get_queryset().filter(product_id=product_id)


class Order(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    product_id = models.CharField(
        max_length=100, 
        db_index=True, 
        blank=False, 
        null=False,
        validators=[validate_not_empty, MinLengthValidator(1)]
    )
    
    product_name = models.CharField(
        max_length=250, 
        blank=False, 
        null=False,
        validators=[validate_not_empty, MinLengthValidator(1)]
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=PENDING, 
        blank=False, 
        null=False
    )
    
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=False, 
        null=False,
    )
    
    stripe_payment_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )

    objects = OrderManager()

    def clean(self):
        super().clean()


class SplitRule(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'
    
    TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage'),
        (FIXED, 'Fixed'),
    ]
    
    order = models.ForeignKey(
        Order, 
        related_name='split_rules',
        on_delete=models.CASCADE, 
        db_index=True
    )
    
    recipient_id = models.CharField(
        max_length=100, 
        db_index=True,
        validators=[validate_not_empty, MinLengthValidator(1)]
    )
    
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        validators=[validate_not_empty]
    )
    
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
    )
    
    account_info = models.JSONField(default=dict)
    effective_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
