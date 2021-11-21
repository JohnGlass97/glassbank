from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Account, ConversionRate, MoneyRequest, ShopItem, Transaction, MAX_REFERENCE_LENGTH, TRANSACTION_LIMIT
from .utils import CURRENCIES


class FirebaseTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=256, error_messages={
                                  "max_length": "Token too long."})


class AccountBasicSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Account
        fields = ['user']


class AccountDetailedSerializer(AccountBasicSerializer):
    class Meta(AccountBasicSerializer.Meta):
        fields = AccountBasicSerializer.Meta.fields + ['balance']


class TransactionSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.user.username')
    recipient = serializers.CharField(source='recipient.user.username')

    class Meta:
        model = Transaction
        exclude = ['epoch', 'sender_bal', 'recip_bal']
        depth = 1


class TransactionDetailedSerializer(TransactionSerializer):
    class Meta(TransactionSerializer.Meta):
        exclude = []


class TransferSerializer(serializers.Serializer):
    amount = serializers.IntegerField(max_value=TRANSACTION_LIMIT, min_value=-TRANSACTION_LIMIT, error_messages={
        "max_value": f"Transaction limit is {TRANSACTION_LIMIT/100}"})
    recipient = serializers.CharField(max_length=150)
    reference = serializers.CharField(max_length=MAX_REFERENCE_LENGTH, error_messages={
        "max_length": "Reference too long."})
    currency = serializers.ChoiceField(choices=list(CURRENCIES.keys()), error_messages={
        "choices": "Invalid currency."})
    epoch = serializers.IntegerField()
    subtract = serializers.BooleanField(default=False)


class MoneyRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(max_value=TRANSACTION_LIMIT, min_value=0, error_messages={
        "min_value": "Can't request negative money.", "max_value": f"Transaction limit is {TRANSACTION_LIMIT/100}"})
    recipient = serializers.CharField(max_length=150)
    reference = serializers.CharField(max_length=MAX_REFERENCE_LENGTH, error_messages={
        "max_length": "Reference too long."})
    currency = serializers.ChoiceField(choices=list(CURRENCIES.keys()), error_messages={
        "choices": "Invalid currency."})


class RequestsSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.user.username')
    recipient = serializers.CharField(source='recipient.user.username')

    class Meta:
        model = MoneyRequest
        fields = '__all__'
        depth = 1


class AnswerRequestSerializer(serializers.Serializer):
    accept = serializers.BooleanField()


class ShopItemSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.user.username')

    class Meta:
        model = ShopItem
        fields = '__all__'
        depth = 1


class BuyItemSerializer(serializers.Serializer):
    price = serializers.IntegerField(min_value=0)


class ConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionRate
        fields = '__all__'
