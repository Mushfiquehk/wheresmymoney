import datetime
from django.db import models


from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, primary_key=True)
    type = models.CharField(max_length=200, choices=[("W", "Weekly"), ("M", "Monthly"), ("Y", "Yearly")])
    budget = models.DecimalField(max_digits=10, decimal_places=2) # daily budget
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("journal:category_detail", kwargs={"pk": self.pk})


class Transaction(models.Model):
    date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tags = models.CharField(max_length=200)  # what it was spent on
    notes = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.tags

    def get_absolute_url(self):
        return reverse("journal:transaction_detail", kwargs={"pk": self.pk})


class Letter(models.Model):
    date = models.DateField(default="2023-12-31")
    body = models.TextField()
    tags = models.CharField(max_length=200)

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

    def get_absolute_url(self):
        return reverse("journal:letter_detail", kwargs={"pk": self.pk})
