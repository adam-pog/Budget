'''GraphQL Schema'''
#pylint: disable=too-few-public-methods
#pylint: disable=missing-class-docstring
#pylint: disable=not-callable
#pylint: disable=no-member
#pylint: disable=missing-function-docstring
#pylint: disable=no-self-argument
#pylint: disable=no-self-use

from datetime import datetime
import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.db.models import Prefetch
from dateutil.relativedelta import relativedelta

from shelf.budget.models import User, MonthlyBudget, Category, Transaction

class UserType(DjangoObjectType):
    '''GraphQL User type'''
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'created',
            'modified'
        )

class TransactionType(DjangoObjectType):
    '''GraphQL Transaction type'''
    class Meta:
        model = Transaction
        fields = (
            'id',
            'created',
            'modified',
            'amount',
            'source',
            'date',
            'recurring',
            'description',
            'category'
        )

class CategoryType(DjangoObjectType):
    '''GraphQL Category type'''
    class Meta:
        model = Category
        fields = (
            'id',
            'label',
            'monthly_amount',
            'created',
            'modified',
            'transactions',
            'budget'
        )

    spent = graphene.Float()
    month = graphene.String()
    year = graphene.String()

    def resolve_spent(self, _):
        '''resolve spent field for CategoryType'''
        return self.spent()

    def resolve_month(self, _):
        '''resolve month field for CategoryType'''
        return self.budget.date.strftime('%B')

    def resolve_year(self, _):
        '''resolve year field for CategoryType'''
        return self.budget.date.strftime('%Y')

class MonthlyBudgetType(DjangoObjectType):
    '''GraphQL Monthly Budget type'''
    class Meta:
        model = MonthlyBudget
        fields = (
            'id',
            'income',
            'categories',
            'user'
        )

    month = graphene.String()
    year = graphene.String()
    net = graphene.Int()

    def resolve_month(self, _):
        '''resolve month field for CategoryType'''
        return self.date.strftime('%B')

    def resolve_year(self, _):
        '''resolve year field for CategoryType'''
        return self.date.strftime('%Y')

    def resolve_net(self, _):
        '''resolve net field for CategoryType'''
        return self.income - sum(c.spent() for c in self.categories.all())

class CreateMonthlyBudget(graphene.Mutation):
    '''GraphQL create Monthly Budget mutation'''
    class Arguments:
        year = graphene.String()
        month = graphene.String()
        income = graphene.Int()

    monthly_budget = graphene.Field(MonthlyBudgetType)

    def mutate(root, info, year, month, income):
        monthly_budget = MonthlyBudget(
            date=datetime.strptime(f'{year} {month}', '%Y %B'),
            income=income,
            user=info.context.user
        )
        monthly_budget.save()

        return CreateMonthlyBudget(monthly_budget=monthly_budget)

class AutoCreateMonthlyBudget(graphene.Mutation):
    '''GraphQL auto create Monthly Budget mutation'''
    monthly_budget = graphene.Field(MonthlyBudgetType)

    def mutate(root, info):
        transaction_prefetch = Prefetch(
            'transactions', queryset=Transaction.objects.filter(recurring=True)
        )
        category_prefetch = Prefetch(
            'categories', queryset=Category.objects.prefetch_related(transaction_prefetch)
        )

        latest_budget = MonthlyBudget.objects.prefetch_related(category_prefetch).filter(
            user=info.context.user
        ).order_by('date').last()

        monthly_budget = MonthlyBudget(
            date=latest_budget.date + relativedelta(months=1),
            income=latest_budget.income,
            user=info.context.user
        )
        monthly_budget.save()
        monthly_budget.copy_from(latest_budget)

        return AutoCreateMonthlyBudget(monthly_budget=monthly_budget)

class CreateCategory(graphene.Mutation):
    '''GraphQL create Category mutation'''
    class Arguments:
        label = graphene.String()
        monthly_amount = graphene.Int()
        budget_id = graphene.ID()

    category = graphene.Field(CategoryType)

    def mutate(root, info, label, monthly_amount, budget_id):
        monthly_budget = MonthlyBudget.objects.get(id=budget_id, user=info.context.user)
        category = Category(
            label=label,
            monthly_amount=monthly_amount,
            budget=monthly_budget
        )
        category.save()

        return CreateCategory(category=category)

class CreateTransaction(graphene.Mutation):
    '''GraphQL create Transaction mutation'''
    class Arguments:
        amount = graphene.Float()
        source = graphene.String()
        day = graphene.Int()
        description = graphene.String()
        category_id = graphene.ID()
        recurring = graphene.Boolean()

    transaction = graphene.Field(TransactionType)

    def mutate(root, info, **fields):
        category = Category.objects.get(budget__user=info.context.user, id=fields['category_id'])
        budget = category.budget

        transaction = category.transactions.create(
            amount=fields['amount'],
            source=fields['source'],
            date=budget.date.replace(day=fields['day']),
            description=fields['description'],
            recurring=fields['recurring']
        )

        return CreateTransaction(transaction=transaction)

class EditTransaction(graphene.Mutation):
    '''GraphQL edit Transaction mutation'''
    class Arguments:
        amount = graphene.Float()
        source = graphene.String()
        day = graphene.Int()
        description = graphene.String()
        recurring = graphene.Boolean()
        id = graphene.ID()

    transaction = graphene.Field(TransactionType)

    def mutate(root, info, **fields):
        transaction = Transaction.objects.get(
            id=fields['id'], category__budget__user=info.context.user
        )
        budget = transaction.category.budget

        transaction.amount = fields['amount']
        transaction.source = fields['source']
        transaction.date = budget.date.replace(day=fields['day'])
        transaction.description = fields['description']
        transaction.recurring = fields['recurring']
        transaction.save()

        return EditTransaction(transaction=transaction)

class EditCategory(graphene.Mutation):
    '''GraphQL edit Category mutation'''
    class Arguments:
        label = graphene.String()
        monthly_amount = graphene.Int()
        id = graphene.ID()

    category = graphene.Field(CategoryType)

    def mutate(root, info, **fields):
        category = Category.objects.get(id=fields['id'], budget__user=info.context.user)
        category.label = fields['label']
        category.monthly_amount = fields['monthly_amount']
        category.save()

        return EditCategory(category=category)

class EditMonthlyBudget(graphene.Mutation):
    '''GraphQL edit Monthly Budget mutation'''
    class Arguments:
        year = graphene.String()
        month = graphene.String()
        income = graphene.Int()
        id = graphene.ID()


    monthly_budget = graphene.Field(MonthlyBudgetType)

    def mutate(root, info, **fields):
        monthly_budget = MonthlyBudget.objects.get(id=fields['id'], user=info.context.user)
        monthly_budget.income = fields['income']
        monthly_budget.date = datetime.strptime(f"{fields['year']} {fields['month']}", '%Y %B')
        monthly_budget.save()
        return EditMonthlyBudget(monthly_budget=monthly_budget)

class DeleteCategory(graphene.Mutation):
    '''GraphQL delete Category mutation'''
    class Arguments:
        id = graphene.ID()

    category = graphene.Field(CategoryType)

    def mutate(root, info, **fields):
        category = Category.objects.get(
            id=fields['id'],
            budget__user=info.context.user
        )
        category.delete()

        return DeleteCategory(category=category)

class DeleteTransaction(graphene.Mutation):
    '''GraphQL delete Transaction mutation'''
    class Arguments:
        id = graphene.ID()

    transaction = graphene.Field(TransactionType)

    def mutate(root, info, **fields):
        transaction = Transaction.objects.get(
            id=fields['id'],
            category__budget__user=info.context.user
        )
        transaction.delete()

        return DeleteTransaction(transaction=transaction)

class DeleteMonthlyBudget(graphene.Mutation):
    '''GraphQL delete Monthly Budget mutation'''
    class Arguments:
        id = graphene.ID()

    monthly_budget = graphene.Field(MonthlyBudgetType)

    def mutate(root, info, **fields):
        monthly_budget = MonthlyBudget.objects.get(
            id=fields['id'],
            user=info.context.user
        )
        monthly_budget.delete()

        return DeleteMonthlyBudget(monthly_budget=monthly_budget)

class Query(graphene.ObjectType):
    '''GraphQL queries'''
    all_categories = graphene.List(CategoryType, budget_id=graphene.ID(required=True))
    monthly_budgets = graphene.List(MonthlyBudgetType, year=graphene.String())
    all_budget_years = graphene.List(graphene.String)
    category = graphene.Field(CategoryType, id=graphene.ID(required=True))
    transaction = graphene.Field(TransactionType, id=graphene.ID(required=True))
    monthly_budget = graphene.Field(MonthlyBudgetType, id=graphene.ID(required=True))

    @login_required
    def resolve_all_categories(self, info, budget_id):
        return Category.objects.prefetch_related('transactions').filter(
            budget_id=budget_id, budget__user=info.context.user
        ).order_by('created')

    @login_required
    def resolve_monthly_budgets(self, info, year):
        return MonthlyBudget.objects.prefetch_related('categories__transactions').filter(
            user=info.context.user, date__year=year
        ).order_by('date__month')

    @login_required
    def resolve_all_budget_years(self, info):
        years = MonthlyBudget.objects.filter(
            user=info.context.user
        ).values_list('date__year').distinct().order_by('-date__year')

        return [year[0] for year in years]

    @login_required
    def resolve_category(self, info, **fields):
        # category also uses transactions when calculating 'spent'.
        # This avoids hitting the db twice when getting 'spent' as well as transaction fields
        prefetch = Prefetch('transactions', queryset=Transaction.objects.order_by('-date'))
        return Category.objects.prefetch_related(prefetch).get(
            id=fields['id'], budget__user=info.context.user
        )

    @login_required
    def resolve_monthly_budget(self, info, **fields):
        return MonthlyBudget.objects.get(id=fields['id'], user=info.context.user)

    @login_required
    def resolve_transaction(self, info, **fields):
        return Transaction.objects.get(id=fields['id'], category__budget__user=info.context.user)

class Mutation(graphene.ObjectType):
    '''GraphQL mutations'''
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    create_monthly_budget = CreateMonthlyBudget.Field()
    auto_create_monthly_budget = AutoCreateMonthlyBudget.Field()
    create_category = CreateCategory.Field()
    create_transaction = CreateTransaction.Field()
    edit_category = EditCategory.Field()
    edit_monthly_budget = EditMonthlyBudget.Field()
    edit_transaction = EditTransaction.Field()
    delete_category = DeleteCategory.Field()
    delete_transaction = DeleteTransaction.Field()
    delete_monthly_budget = DeleteMonthlyBudget.Field()
    # verify_token = graphql_jwt.Verify.Field()
    # refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
