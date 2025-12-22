from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),

    # Products App
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    
    path('baskets/add/', views.BasketCreateView.as_view(), name='basket_create'),
    
    path('merch/', views.MerchList.as_view(), name='merch_list'),
    path('merch/add/', views.MerchCreate.as_view(), name='merch_create'),
    path('merch/<int:pk>/edit/', views.MerchUpdate.as_view(), name='merch_update'),

    path('recipes/', views.RecipeList.as_view(), name='recipe_list'),
    path('recipes/add/', views.RecipeCreate.as_view(), name='recipe_create'),
    path('recipes/<slug:slug>/edit/', views.RecipeUpdate.as_view(), name='recipe_update'),

    # Cart App
    path('carts/', views.CartListView.as_view(), name='cart_list'),

    # Checkout App
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),

    path('zones/', views.ZoneList.as_view(), name='zone_list'),
    path('zones/add/', views.ZoneCreate.as_view(), name='zone_create'),
    path('zones/<int:pk>/edit/', views.ZoneUpdate.as_view(), name='zone_update'),

    # Core App
    path('gallery/categories/', views.GalCatList.as_view(), name='gallery_cat_list'),
    path('gallery/categories/add/', views.GalCatCreate.as_view(), name='gallery_cat_create'),
    path('gallery/categories/<int:pk>/edit/', views.GalCatUpdate.as_view(), name='gallery_cat_edit'),

    path('gallery/items/', views.GalItemList.as_view(), name='gallery_item_list'),
    path('gallery/items/add/', views.GalItemCreate.as_view(), name='gallery_item_create'),
    path('gallery/items/<int:pk>/edit/', views.GalItemUpdate.as_view(), name='gallery_item_edit'),

    path('popups/', views.PopupList.as_view(), name='popup_list'),
    path('popups/add/', views.PopupCreateView.as_view(), name='popup_create'),
    path('popups/<int:pk>/edit/', views.PopupUpdateView.as_view(), name='popup_edit'),
]