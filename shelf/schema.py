import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from shelf.budget.models import *

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'monthly_income',
            'created',
            'modified'
        )

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = (
            'id',
            'label',
            'monthly_amount',
            'user',
            'created',
            'modified',
            'transactions'
        )

    spent = graphene.Float()

    def resolve_spent(instance, info):
        return instance.spent()

class TransactionType(DjangoObjectType):
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

class CreateCategory(graphene.Mutation):
    class Arguments:
        label = graphene.String()
        monthly_amount = graphene.Int()

    category = graphene.Field(CategoryType)

    def mutate(root, info, label, monthly_amount):
        category = Category(
            label=label,
            monthly_amount=monthly_amount,
            user=info.context.user
        )
        category.save()

        return CreateCategory(category=category)

class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    category = graphene.Field(CategoryType)

    def mutate(root, info, id):
        category = Category.objects.get(
            id=id,
            user=info.context.user
        )
        category.delete()

        return DeleteCategory(category=category)


class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.ID(required=True))

    @login_required
    def resolve_all_categories(self, info):
        return Category.objects.prefetch_related('transactions').filter(user=info.context.user)

    @login_required
    def resolve_category(self, info, id):
        return Category.objects.get(id=id)

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    create_category = CreateCategory.Field()
    delete_category = DeleteCategory.Field()
    # verify_token = graphql_jwt.Verify.Field()
    # refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
