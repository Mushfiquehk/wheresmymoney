"""Views to add, update, delete, transactions and categories
and view summaries of transactions by category"""
import datetime
import calendar
from decimal import Decimal

# Create your views here.
from django.http import HttpResponse
from django.template import loader

from .models import Transaction, Category, Letter
from .forms import TransactionForm, CategoryForm, LetterForm

from django.views import generic
from django.db.models import Sum

# Utility class for budget calculations
class BudgetCalculator:
    """Helper class to calculate budget-related data based on time periods."""

    NAME_TIME_FACTOR = {
        "W": Decimal(7),
        "M": Decimal(30),
        "Y": Decimal(365),
    }
    
    TIME_NAME = {
        "W": "Week",
        "M": "Month",
        "Y": "Year",
    }

    @classmethod
    def get_date_range(cls, time_period: str):
        """Calculate start and end dates for the given time period."""
        if time_period == "W":
            start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
            end_date = start_date + datetime.timedelta(days=6)
        elif time_period == "M":
            start_date = datetime.date.today().replace(day=1)
            end_date = start_date + datetime.timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1])
        elif time_period == "Y":
            start_date = datetime.date.today().replace(month=1, day=1)
            end_date = start_date + datetime.timedelta(days=364)
        else:
            raise ValueError("Invalid time period")
        
        return start_date, end_date

    @classmethod
    def calculate_income(cls, time_period: str, start_date: datetime.date, end_date: datetime.date):
        """Calculate actual and anticipated incomes."""
        actual_income_transactions = Transaction.objects.filter(
            amount__lt=0,
            date__range=[start_date, end_date]
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        actual_income = round(actual_income_transactions / cls.NAME_TIME_FACTOR[time_period] * cls.NAME_TIME_FACTOR[time_period], 2)

        anticipated_income = sum(
            round(category.budget / cls.NAME_TIME_FACTOR[category.type] * cls.NAME_TIME_FACTOR[time_period], 2)
            for category in Category.objects.filter(budget__lt=0)
        )
        
        return actual_income, anticipated_income

    @classmethod
    def categorize_expenses(cls, start_date: datetime.date, end_date: datetime.date, time_period: str):
        """Categorize expenses by budget and transactions."""
        req_expense_type = ['W'] if time_period == "W" else ['W', 'M'] if time_period == "M" else ['W', 'M', 'Y']
        all_expenses = Category.objects.filter(type__in=req_expense_type).order_by("budget")
        
        all_transactions = Transaction.objects.filter(date__range=[start_date, end_date])
        category_transactions = {}

        for category in all_expenses:
            category_transactions[category.name] = {
                "budget": round(category.budget / cls.NAME_TIME_FACTOR[category.type] * cls.NAME_TIME_FACTOR[time_period], 2),
                "transactions": [],
                "total_spent": Decimal(0),
            }

            category_month_transactions = all_transactions.filter(category=category).order_by("-date")

            for transaction in category_month_transactions:
                category_transactions[category.name]["transactions"].append(transaction)
                category_transactions[category.name]["total_spent"] += transaction.amount
        
        return category_transactions


def index(request):
    """Index view to display latest transactions."""
    template = loader.get_template("journal/index.html")
    context = {
        "latest_transactions": Transaction.objects.order_by("-date")[:5],
    }
    return HttpResponse(template.render(context, request))


def show_budget(request, time_period: str):
    """Displays budget and transaction summary by category for a given time period."""
    start_date, end_date = BudgetCalculator.get_date_range(time_period)
    
    actual_income, anticipated_income = BudgetCalculator.calculate_income(time_period, start_date, end_date)
    category_transactions = BudgetCalculator.categorize_expenses(start_date, end_date, time_period)

    anticipated_expenses = sum(cat["budget"] for cat in category_transactions.values() if cat["budget"] >= 0)
    actual_expenses = sum(cat["total_spent"] for cat in category_transactions.values())
    
    template = loader.get_template("journal/budget.html")
    context = {
        "time_name": BudgetCalculator.TIME_NAME[time_period],
        "category_transactions": category_transactions,
        "anticipated_income": -anticipated_income,
        "actual_income": -actual_income,
        "anticipated_expenses": anticipated_expenses,
        "actual_expenses": actual_expenses,
        "net_income": -actual_income + anticipated_income,
        "net_expenses": actual_expenses - anticipated_expenses,
        "anticipated_net_worth": -anticipated_income - anticipated_expenses,
        "actual_net_worth": -actual_income - actual_expenses,
    }
    return HttpResponse(template.render(context, request))


# CRUD views for categories
class CategoryCreateView(generic.CreateView):
    model = Category
    template_name = "journal/category_create.html"
    context_object_name = "category"
    form_class = CategoryForm
    success_url = "/"


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = "journal/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = Transaction.objects.filter(
            category=self.object
        ).order_by("-date")
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


# CRUD views for transactions
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


# CRUD views for letters
class LetterCreateView(generic.CreateView):
    model = Letter
    template_name = "journal/letter_create.html"
    context_object_name = "letter"
    form_class = LetterForm
    success_url = "/"


class LetterDetailView(generic.DetailView):
    model = Letter
    template_name = "journal/letter_detail.html"
    context_object_name = "letter"


class LetterUpdateView(generic.UpdateView):
    model = Letter
    template_name = "journal/letter_update.html"
    context_object_name = "letter"
    form_class = LetterForm


class LetterDeleteView(generic.DeleteView):
    model = Letter
    template_name = "journal/letter_delete.html"
    context_object_name = "letter"
    success_url = "/"
