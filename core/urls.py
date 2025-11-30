from django.urls import path
from .views import (
    HomeView
)


urlpatterns = [

    # Main Pages
    path('', HomeView.as_view(), name='home'),

]