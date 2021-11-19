import requests
import traceback
import pytz
import json

from rest_framework import pagination
from rest_framework.response import Response
from datetime import datetime, timedelta

FIREBASE_SERVER_KEY = "AAAAlchymSI:APA91bFVS74kyLabhXD70Ns1U8zvgOlAIs2vJLUrjlzaOQJPiGkSJApxSsFDSrG3Pj9_gNvDGtfnSLj6z5ULKvLH-tqXxEEvnYt6Xgt7gQ9kkAKmEVp7-lgvv95UIb5RAQPT9_xx2ryr"

CURRENCIES = {
    "GBP": "£",
    "EUR": "€"
}

utc = pytz.UTC


class PlainPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(data)


def detailed_exception_handler(exc, context):
    print(traceback.format_exc())
    return Response({"error": str(exc)}, status=500)


def join_serializer_errors(errors):
    output = ""
    for arr in errors.values():
        for x in arr:
            output += x+"\n"
    return {"error": output}


def conversion_to_GBP(currency):
    from .models import ConversionRate
    if currency == "GBP":
        return 1.0
    assert currency in CURRENCIES.keys()

    time = utc.localize(datetime.now())
    try:
        obj = ConversionRate.objects.get(currency=currency)
        if obj.timestamp + timedelta(days=1) > time:
            return obj.rate
    except ConversionRate.DoesNotExist:
        pass
    try:
        query = currency + "_GBP"
        response = requests.get(
            f"https://free.currconv.com/api/v7/convert?q={query}&compact=ultra&apiKey=ab9dc965f40bbecb5a1a")
        rate = float(response.json()[query])
        obj, c = ConversionRate.objects.get_or_create(currency=currency)
        obj.rate = rate
        obj.save()
        return rate
    except:
        print(traceback.format_exc())
        assert obj.timestamp + timedelta(weeks=1) < time
        return obj.rate


def int_to_GBP(value, currency):
    return round(value*conversion_to_GBP(currency))


def format_currency(value, currency):
    sign = "-" if value < 0 else ""
    return f"{sign}{CURRENCIES[currency]}{abs(value)/100:.2f}"


def send_notification(f_id, title, body):
    print(title, body)
    URL = "https://fcm.googleapis.com/fcm/send"
    data = {
        "to": f_id,
        "notification": {
            "title": title,
            "body": body
        }
    }
    headers = {
        "Authorization": "key=" + FIREBASE_SERVER_KEY,
        "Content-Type":  "application/json"
    }
    return requests.post(URL, data=json.dumps(data), headers=headers)


def bulkCreate():
    from apps.banking.models import Account, Transaction
    for i in range(100):
        acc = Account.objects.get(user_id=1)
        obj = Transaction.objects.create(
            sender=acc, recipient=acc, amount=0, reference=str(i), sender_bal=0, recip_bal=0)
        obj.save()
