from rest_framework.exceptions import APIException
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import format_currency, send_notification, int_to_GBP

MAX_REFERENCE_LENGTH = 100
TRANSACTION_LIMIT = 100000


class Account(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    balance = models.IntegerField(default=0)
    master = models.BooleanField(default=False)
    firebase = models.CharField(max_length=256, blank=True, default="")

    def __str__(self):
        balance = format_currency(self.balance, "GBP")
        return f"{self.user}: {balance}"

    def notify(self, title, body):
        if self.firebase != "":
            return send_notification(self.firebase, title, body)


class Transaction(models.Model):
    sender = models.ForeignKey(Account, models.RESTRICT, related_name='sent')
    recipient = models.ForeignKey(
        Account, models.RESTRICT, related_name='received')
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=MAX_REFERENCE_LENGTH)
    time = models.DateTimeField(auto_now_add=True)
    epoch = models.IntegerField(null=True)
    sender_bal = models.IntegerField()
    recip_bal = models.IntegerField()

    class Meta:
        ordering = ['-id']

    @classmethod
    def transfer(cls, sender, recip, amount, ref, epoch, currency="GBP"):
        pennies = int_to_GBP(amount, currency)
        if epoch is not None:
            matches = Transaction.objects.filter(
                sender=sender, recipient=recip, reference=ref, epoch=epoch).count()
            if matches > 0:
                if matches > 1:
                    raise APIException("Duplicate Transaction Found!", 500)
                return
        if sender != recip:
            sender.balance -= pennies
            sender.save()
            recip.balance += pennies
            recip.save()
        transaction = cls(sender=sender, recipient=recip, amount=pennies,
                          reference=ref, epoch=epoch, sender_bal=sender.balance, recip_bal=recip.balance)
        transaction.save()
        formatted_amount = format_currency(amount, currency)
        recip.notify("Money Received",
                     f"Received {formatted_amount} from {sender.user}")

    def __str__(self):
        amount = format_currency(self.amount, "GBP")
        sender = self.sender.user
        recip = self.recipient.user
        sender_bal = format_currency(self.sender_bal, "GBP")
        recip_bal = format_currency(self.recip_bal, "GBP")
        return f"{sender} -> {recip} : {amount} - {self.reference[:20]} at {self.time}, {sender}: {sender_bal}, {recip}: {recip_bal}"


class MoneyRequest(models.Model):
    sender = models.ForeignKey(
        Account, models.RESTRICT, related_name='requests_sent')
    recipient = models.ForeignKey(
        Account, models.RESTRICT, related_name='requests_received')
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=MAX_REFERENCE_LENGTH)

    def __str__(self):
        amount = format_currency(self.amount, "GBP")
        return f"{self.sender.user} -> {self.recipient.user} : {amount} - {self.reference[:20]}"

    def accept(self):
        Transaction.transfer(self.recipient, self.sender,
                             self.amount, self.reference, None)

    @classmethod
    def request(cls, sender, recip, amount, ref, currency):
        pennies = int_to_GBP(amount, currency)
        moneyRequest = cls(sender=sender, recipient=recip, amount=pennies,
                           reference=ref)
        moneyRequest.save()
        formatted_amount = format_currency(amount, currency)
        recip.notify("Money Requested",
                     f"{sender.user} has requested {formatted_amount}")


class ShopItem(models.Model):
    name = models.CharField(max_length=30)
    price = models.PositiveIntegerField()
    owner = models.ForeignKey(Account, models.RESTRICT,
                              related_name='shop_items')

    def buy(self, buyer):
        Transaction.transfer(buyer, self.owner,
                             self.price, f"Shop Item: {self.name}", None)

    def __str__(self) -> str:
        price = format_currency(self.price, "GBP")
        return f"{self.name}: {price} owned by {self.owner.user}"


class ConversionRate(models.Model):
    currency = models.CharField(max_length=3)
    rate = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.currency} to GBP: {self.rate} last updated at {self.timestamp}"


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_account(sender, instance, **kwargs):
    instance.account.save()
