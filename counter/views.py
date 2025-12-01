from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .models import Order


@never_cache
def index(request):
    """Главная view функция"""
    orders = Order.objects.all()
    response = render(request, 'counter/index.html', {'orders': orders})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
