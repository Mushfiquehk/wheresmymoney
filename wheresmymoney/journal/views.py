"""Views to add, update, delete, transactions and categories
and view summaries of transactions by category"""
import datetime
from decimal import Decimal
from typing import Any

# Create your views here.
from django.http import HttpResponse
from django.template import loader

from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm

from django.views import generic


def index(request):
    """ Displays a summary of transactions by category for the current week

    Args:
        request (_type_): _description_

    Returns:
        dict: 
        category_transactions: {
            name: {
                budget: number
                transactions: [
                    {
                        date: string,
                        amount: number,
                        description: string
                    },
                    ...
                ]
                total: number
            }
        }
    """    

    week_start = datetime.date.today() - datetime.timedelta(
        days=datetime.date.today().weekday()
    )
    week_end = week_start + datetime.timedelta(days=6)

    # get all categories and transactions for the week
    category_transactions = Category.objects.all()

    all_categories = Category.objects.all()    
    weeks_transactions = Transaction.objects.filter(date__range=[week_start, week_end])

    category_transactions = {}
    for category in all_categories:
        category_transactions[category.name] = {
            "budget": category.budget,
            "transactions": [],
            "total_spent": 0,
        }

    for transaction in weeks_transactions:

        if transaction.category not in category_transactions:
            category_transactions[transaction.category] = {
                "budget": -1,
                "transactions": [],
                "total_spent": 0,
            }

        category_transactions[transaction.category]["transactions"].append(
            {
                "date": transaction.date,
                "amount": transaction.amount,
                "tags": transaction.tags,
                "notes": transaction.notes,
                "category": transaction.category,
                "id": transaction.id,
            }
        )
        category_transactions[transaction.category]["total_spent"] += transaction.amount


    template = loader.get_template("journal/index.html")
    context = {
        "category_transactions": category_transactions,
        "latest_transactions": Transaction.objects.order_by("-date")[:5],
    }
    return HttpResponse(template.render(context, request))


class CategoryCreateView(generic.CreateView):
    model = Category
    template_name = "journal/category_create.html"
    context_object_name = "category"
    form_class = CategoryForm

class CategoryListView(generic.ListView):
    ''' Returns the list of transactions for a given category '''    
    model = Category
    template_name = "journal/category_list.html"
    context_object_name = "category_list"

    def get_queryset(self):
        return Category.objects.all()

class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = "journal/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = Transaction.objects.filter(category=self.object).order_by("-date")
        return context

class CategoryUpdateView(generic.UpdateView):
    model = Category
    template_name = "journal/category_update.html"
    context_object_name = "category"
    form_class = CategoryForm
    success_url = "/"
    
class CategoryDeleteView(generic.DeleteView):
    model = Category
    template_name = "journal/category_delete.html"
    context_object_name = "category"
    success_url = "/"


class TransactionCreateView(generic.CreateView):
    model = Transaction
    template_name = "journal/transaction_create.html"
    context_object_name = "transaction"
    form_class = TransactionForm
    success_url = "/"

class TransactionDetailView(generic.DetailView):
    model = Transaction
    template_name = "journal/transaction_detail.html"
    context_object_name = "transaction"

class TransactionUpdateView(generic.UpdateView):
    model = Transaction
    template_name = "journal/transaction_update.html"
    context_object_name = "transaction"
    form_class = TransactionForm

class TransactionDeleteView(generic.DeleteView):
    model = Transaction
    template_name = "journal/transaction_delete.html"
    context_object_name = "transaction"
    success_url = "/"

    

    success_url = "/"
    
    