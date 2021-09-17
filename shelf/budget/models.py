'''Models for budget app (User, MonthlyBudget, Category, Transaction)'''

from django.db import models
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    '''User model for authentication'''

    first_name = None
    last_name = None

class MonthlyBudget(TimeStampedModel):
    '''Represents a budget for a given month/year'''

    user = models.ForeignKey(
        User,
        related_name='budgets',
        on_delete=models.CASCADE
    )
    income = models.IntegerField()
    date = models.DateField()

    def copy_from(self, other_budget):
        '''Copies categories and recurring transactions from another budget'''
        categories = other_budget.categories.all()

        for category in categories:
            transactions = category.transactions.all()
            category.id = None
            category.budget = self
            category.save()

            for transaction in transactions:
                transaction.id = None
                transaction.category = category
                transaction.save()

class Category(TimeStampedModel):
    '''Represents a specific category for a budget (i.e. food, rent, etc.)'''

    verbose_name_plural = "categories"

    label = models.CharField(max_length=100)
    budget = models.ForeignKey(
        MonthlyBudget,
        related_name='categories',
        on_delete=models.CASCADE
    )
    monthly_amount = models.IntegerField()

    def __str__(self):
        return self.label

    def spent(self):
        '''Calculates the cost of all related transactions'''
        return sum(t.amount for t in self.transactions.all())

class Transaction(TimeStampedModel):
    '''Represents a specific transaction in a given day'''

    amount = models.FloatField()
    source = models.CharField(max_length=100)
    date = models.DateField()
    recurring = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category,
        related_name='transactions',
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description
