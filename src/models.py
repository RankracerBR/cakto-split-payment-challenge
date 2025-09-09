from django.db import models


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
    
    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SplitRule(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'
    
    TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage'),
        (FIXED, 'Fixed'),
    ]
    
    order = models.ForeignKey(Order, related_name='split_rules', on_delete=models.CASCADE)
    recipient_id = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    account_info = models.JSONField(default=dict)
    effective_date = models.DateTimeField(auto_now_add=True)
