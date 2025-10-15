from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("save/", views.save_bill, name="save_bill"),
    path("invoice/<int:bill_id>/", views.invoice_preview, name="invoice_preview"),
    path('invoice/<int:bill_id>/send/', views.send_bill_email, name='send_bill_email'),
]
