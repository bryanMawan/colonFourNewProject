# selectors.py
from .models import Dancer

def get_all_dancers():
    return Dancer.objects.all()
