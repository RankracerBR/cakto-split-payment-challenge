from rest_framework import serializers
from .models import SplitRuleModel, SplitPaymentModel


class SplitRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SplitRuleModel
        fields = ['recipient_id', 'type', 'value', 'account_info']


class SplitPaymentSerializer(serializers.ModelSerializer):
    rules = SplitRuleSerializer(many=True)
    
    class Meta:
        model = SplitPaymentModel
        fields = ['product_id', 'rules', 'effective_date', 'total_amount']
    
    def validate_rules(self, value):
        total_percentage = sum(rule['value'] for rule in value if rule['type'] == 'percentage')
        if total_percentage > 100:
            raise serializers.ValidationError("Total percentage cannot exceed 100%")
        return value
