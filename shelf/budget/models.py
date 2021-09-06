from django.db import models
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    first_name = None
    last_name = None
    monthly_income = models.IntegerField()

class Category(TimeStampedModel):
    verbose_name_plural = "categories"

    label = models.CharField(max_length=100)
    user = models.ForeignKey(
        User,
        related_name='categories',
        on_delete=models.CASCADE
    )
    monthly_amount = models.IntegerField()

    def __str__(self):
        return self.label

    def spent(self):
        return 500

class Transaction(TimeStampedModel):
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
