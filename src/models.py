from django.db import models
from django.core.validators import MinValueValidator


class SplitRuleModel(models.Model):
    RULE_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    recipient_id = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=10, choices=RULE_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    account_info = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class SplitPaymentModel(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    product_id = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    rules = models.ManyToManyField(SplitRuleModel)
    effective_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'effective_date']),
            models.Index(fields=['transaction_id']),
        ]
        

class PaymentLog(models.Model):
    split_payment = models.ForeignKey(SplitPaymentModel, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
