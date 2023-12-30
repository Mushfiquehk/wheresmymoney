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



def index(request):
    """ """
    template = loader.get_template("journal/index.html")
    context = {
        "latest_transactions": Transaction.objects.order_by("-date")[:5],
    }
    return HttpResponse(template.render(context, request))


def show_budget(request, time_period: str):
    """Displays each category's budget, trasanctions, and total spent for the month

    Args:
        request (HttpRequest): The request object

    Returns:
        category_transactions = {
            "category_name": {
                "budget": 0,
                "transactions": [],
                "total_spent": 0,
            },
    ...}
    """
    # each type descriptor of category tells its expense frequency
    name_time_factor = {
        "W": Decimal(7),
        "M": Decimal(30),
        "Y": Decimal(365),
    }
    time_name = {
        "W": "Week",
        "M": "Month",
        "Y": "Year",
    }
    num_days = name_time_factor[time_period]
    start_date  = 0
    end_date = 0

    # set dates to get transactions
    if time_period == "W":    
        start_date = datetime.date.today() - datetime.timedelta(
            days=datetime.date.today().weekday()
        )
        end_date = start_date + datetime.timedelta(days=6)
    elif time_period == "M":
        start_date = datetime.date.today().replace(day=1)
        end_date = start_date + datetime.timedelta(
            days=calendar.monthrange(start_date.year, start_date.month)[1]
        )
    elif time_period == "Y":
        start_date = datetime.date.today().replace(month=1, day=1)
        end_date = start_date + datetime.timedelta(days=364)

    # get total actual income
    actual_income = 0
    actual_income_transactions = Transaction.objects.filter(
                                amount__lt=0,
                                date__range=[start_date, end_date]
                                ).aggregate(Sum("amount"))["amount__sum"]
    actual_income = round(actual_income_transactions / name_time_factor[time_period]
                    * num_days,
                    2,
                    ) if actual_income is not None else 0
    
    # get anticipated income
    anticipated_income = 0
    anticipated_income_categories = Category.objects.filter(
                        budget__lt=0,
                        )
    if anticipated_income_categories:
        for category in anticipated_income_categories:
            anticipated_income += round(category.budget / name_time_factor[category.type] * num_days, 2)
    
    # get all categories and transactions
    # iter over cats and calc budget, expenses (during time period)
    # and add transactions to respective categories
    req_expense_type = ['W', 'M', 'Y']
    if time_period == "W":
        req_expense_type = ['W']
    if time_period == "M":
        req_expense_type = ['W', 'M']
    all_expenses = Category.objects.filter(
        type__in=req_expense_type
    ).order_by("budget")
    all_transactions = Transaction.objects.filter(
        date__range=[start_date, end_date]
    )

    # NOTE transactions without a category are not included

    anticipated_expenses = 0
    actual_expenses = 0
    category_transactions = {}
    for category in all_expenses:
        category_transactions[category.name] = {
            "budget": round(
                category.budget / name_time_factor[category.type] * num_days, 2
            ),
            "transactions": [],
            "total_spent": Decimal(0),
        }
        if category.budget >= 0:
            anticipated_expenses += round(category.budget / name_time_factor[category.type] * num_days, 2)

        category_month_transactions = all_transactions.filter(category=category).order_by(
            "-date"
        )
        for transaction in category_month_transactions:
            category_transactions[transaction.category.name]["transactions"].append(
                transaction
            )
            category_transactions[transaction.category.name][
                "total_spent"
            ] += transaction.amount
            if category.budget >= 0:
                actual_expenses += transaction.amount

    template = loader.get_template("journal/budget.html")
    context = {
        "time_name": time_name[time_period],
        "category_transactions": category_transactions,
        "anticipated_income": - anticipated_income,
        "actual_income": - actual_income,
        "anticipated_expenses": anticipated_expenses,
        "actual_expenses": actual_expenses,
        "net_income": - actual_income + anticipated_income,
        "net_expenses": actual_expenses - anticipated_expenses,
        "anticipated_net_worth": - anticipated_income - anticipated_expenses,
        "actual_net_worth": - actual_income - actual_expenses,
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
