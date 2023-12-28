from django import forms

from .models import Transaction, Category


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'tags', 'notes', 'category']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'budget', 'type', 'parent']