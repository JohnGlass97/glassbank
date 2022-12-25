import random
from django.db import models

from apps.banking.models import Account, Transaction
from apps.banking.utils import format_currency


class GiftCard(models.Model):
    sender = models.ForeignKey(
        Account, models.RESTRICT, related_name='giftcards_sent')
    recipient = models.ForeignKey(
        Account, models.RESTRICT, related_name='giftcards_received')
    amount = models.PositiveIntegerField()
    code = models.CharField(max_length=8,
                            default=str(random.randint(0, 999999)).zfill(6), unique=True)
    redeemed = models.BooleanField(default=False)

    def __str__(self):
        amount = format_currency(self.amount, "GBP")
        return f"{self.sender.user} -> {self.recipient.user} : {amount} - {self.code}"

    def gen_reference(self):
        return f"Gift Card redeemed, Merry Christmas!"

    def redeem(self):
        if self.redeemed:
            return
        self.redeemed = True
        self.save()
        Transaction.transfer(self.sender, self.recipient,
                             self.amount, self.gen_reference(), None)
