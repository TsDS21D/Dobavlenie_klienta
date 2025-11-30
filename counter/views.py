from django.shortcuts import render
from .models import Order

def index(request):
    """
    Главная view функция.
    Она обрабатывает HTTP GET запрос на /
    """
    orders = Order.objects.all()
    return render(request, 'counter/index.html', {'orders': orders})