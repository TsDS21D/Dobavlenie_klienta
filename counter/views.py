from django.shortcuts import render
from .models import ClickCounter

def index(request):
    counter = ClickCounter.get_current_count()
    return render(request, 'counter/index.html', {'count': counter})
