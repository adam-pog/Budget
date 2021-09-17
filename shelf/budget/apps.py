'''Contains BudgetConfig'''

from django.apps import AppConfig

class BudgetConfig(AppConfig):
    '''configuration for budget app'''

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shelf.budget'
