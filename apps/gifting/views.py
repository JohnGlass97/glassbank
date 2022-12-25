from django.shortcuts import render
from apps.banking.utils import format_currency

from apps.gifting.models import GiftCard

from .forms import RedeemForm


def redeem(request):
    err = "Enter code above"
    if request.method == "POST":
        form = RedeemForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                gift_card = GiftCard.objects.get(code=code)
                data = {
                    "sender": gift_card.sender.user,
                    "recip": gift_card.recipient.user,
                    "amount": format_currency(gift_card.amount, "GBP")
                }
                gift_card.redeem()
                return render(request, 'success.html', data)
            except GiftCard.DoesNotExist:
                pass
        err = "Invalid code"
    else:
        form = RedeemForm()
    return render(request, 'redeem.html', {'form': form, 'error': err})
