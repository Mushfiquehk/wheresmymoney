from django import forms

from .models import Transaction, Category, Letter


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["date", "amount", "tags", "notes", "category"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "budget", "type", "parent"]


class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ["date", "body", "tags"]
