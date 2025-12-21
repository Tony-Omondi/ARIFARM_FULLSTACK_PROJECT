# core/context_processors.py
from .models import PromotionalPopup

def promotional_popup(request):
    popup = PromotionalPopup.get_active_popup()
    return {'promotional_popup': popup}