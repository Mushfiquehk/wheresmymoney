from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.index, name='index'),
    path('transaction/create', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transaction/<str:pk>/detail', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transaction/<str:pk>/update', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transaction/<str:pk>/delete', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    path('category/create', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<str:pk>/detail', views.CategoryDetailView.as_view(), name='category_detail'), 
    path('category/<str:pk>/update', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<str:pk>/delete', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('letter/create', views.LetterCreateView.as_view(), name='letter_create'),

    path('budget/<str:time_period>', views.show_budget, name='budget_show'),
]
