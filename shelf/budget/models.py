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
        related_name='budget_categories',
        on_delete=models.CASCADE
    )
    monthly_amount = models.IntegerField()

    def spent(self):
        return 100

    def progress(self):
        return 40
