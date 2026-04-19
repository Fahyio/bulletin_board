from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.index, name='index'),
    path('ad/<int:pk>/', views.ad_detail, name='detail'),
    path('ad/create/', views.ad_create, name='create'),
    path('ad/<int:pk>/edit/', views.ad_edit, name='edit'),
    path('ad/<int:pk>/delete/', views.ad_delete, name='delete'),
    path('ad/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('my-ads/', views.my_ads, name='my_ads'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
