from django.urls import path

from .views import *

urlpatterns = [
    path('accounts', AccountsView.as_view()),
    path('transactions', TransactionsView.as_view()),
    path('transfer', TransferView.as_view()),
    path('firebase', SetFirebaseTokenView.as_view()),
    path('requests', RequestsView.as_view()),
    path('requests/<int:pk>', AnswerRequestView.as_view()),
    path('shop', ShopItemsView.as_view()),
    path('shop/<int:pk>', BuyItemView.as_view()),
    path('conversion', ConversionToGBPView.as_view()),
    path('backup', BackupView.as_view())
]
