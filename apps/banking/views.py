from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.banking.utils import join_serializer_errors

from .models import Account, ConversionRate, MoneyRequest, ShopItem, Transaction
from .serializers import *


class AccountsView(APIView):
    def get(self, request):
        if request.GET.get('me', False):
            serializer = AccountDetailedSerializer(request.user.account)
            return Response(serializer.data)
        queryset = Account.objects.all()
        if request.user.account.master:
            serializer = AccountDetailedSerializer(queryset, many=True)
        else:
            serializer = AccountBasicSerializer(queryset, many=True)
        return Response(serializer.data)


class TransferView(APIView):
    def post(self, request):
        data = TransferSerializer(data=request.data)
        if not data.is_valid():
            return Response(join_serializer_errors(data.errors), status=400)
        sender = request.user.account
        try:
            recipient = User.objects.get(
                username=data.validated_data['recipient']).account
        except User.DoesNotExist:
            return Response("No Such User!", 400)
        amount = abs(data.validated_data['amount'])
        if data.validated_data['subtract']:
            if not sender.master:
                return Response(status=403)
            sender, recipient = recipient, sender
        Transaction.transfer(sender, recipient, amount,
                             data.validated_data['reference'], data.validated_data['epoch'], data.validated_data['currency'])
        return Response(status=200)


class RequestsView(APIView):
    def post(self, request):
        data = MoneyRequestSerializer(data=request.data)
        if not data.is_valid():
            return Response(join_serializer_errors(data.errors), status=400)
        sender = request.user.account
        try:
            recipient = User.objects.get(
                username=data.validated_data['recipient']).account
        except User.DoesNotExist:
            return Response("No Such User!", 400)
        amount = data.validated_data['amount']
        MoneyRequest.request(sender, recipient, amount,
                             data.validated_data['reference'], data.validated_data['currency'])
        return Response(status=200)

    def get(self, request):
        account = request.user.account
        queryset = MoneyRequest.objects.filter(recipient=account)
        serializer = RequestsSerializer(queryset, many=True)
        return Response(serializer.data)


class AnswerRequestView(APIView):
    def post(self, request, pk):
        data = AnswerRequestSerializer(data=request.data)
        if not data.is_valid():
            return Response(join_serializer_errors(data.errors), status=400)
        queryset = MoneyRequest.objects.all()
        moneyRequest = generics.get_object_or_404(queryset, id=pk)
        if moneyRequest.recipient != request.user.account:
            return Response(status=403)
        if data.validated_data['accept']:
            moneyRequest.accept()
        moneyRequest.delete()
        return Response(status=200)


class SetFirebaseTokenView(APIView):
    def post(self, request):
        data = FirebaseTokenSerializer(data=request.data)
        if not data.is_valid():
            return Response(join_serializer_errors(data.errors), status=400)
        account = request.user.account
        account.firebase = data.validated_data['token']
        account.save()
        return Response(status=200)


class TransactionsView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_fields = {
        'id': ['gt', 'lt'],
        'amount': ['gt', 'lt'],
        'sender': ['exact'],
        'recipient': ['exact'],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        account = self.request.user.account
        if not account.master:
            queryset = queryset.filter(
                Q(sender=account) | Q(recipient=account))
        return queryset


class ShopItemsView(generics.ListAPIView):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer


class BuyItemView(APIView):
    def post(self, request, pk):
        data = BuyItemSerializer(data=request.data)
        if not data.is_valid():
            return Response(join_serializer_errors(data.errors), status=400)
        buyer = request.user.account
        item = ShopItem.objects.get(id=pk)
        if item.price != data.validated_data['price']:
            return Response("Price of this item has changed.", status=400)
        item.buy(buyer)
        return Response(status=200)


class ConversionToGBPView(APIView):
    def get(self, request):
        conversion = generics.get_object_or_404(
            ConversionRate.objects.all(), currency=request.GET.get('currency', "EUR"))
        serializer = ConversionSerializer(conversion)
        return Response(serializer.data)


class BackupView(APIView):
    def get(self, request):
        if not request.user.account.master:
            return Response(status=403)
        accountSerializer = AccountDetailedSerializer(
            Account.objects.all(), many=True)
        transactionSerializer = TransactionDetailedSerializer(
            Transaction.objects.all(), many=True)
        return Response({"accounts": accountSerializer.data, "transactions": transactionSerializer.data})
