from django.db import models

from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, primary_key=True)
    type = models.CharField(max_length=200)
    budget = models.FloatField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    tags = models.CharField(max_length=200)
    notes = models.CharField(max_length=200)
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.tags
