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
        )

    spent = graphene.Int()
    def resolve_spent(instance, info):
        return instance.spent()

class CreateCategory(graphene.Mutation):
    class Arguments:
        label = graphene.String()
        monthly_amount = graphene.Int()

    category = graphene.Field(lambda: CategoryType)

    def mutate(root, info, label, monthly_amount):
        category = Category(
            label=label,
            monthly_amount=monthly_amount,
            user=info.context.user
        )
        category.save()

        return CreateCategory(category=category)


class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)

    @login_required
    def resolve_all_categories(self, info):
        return Category.objects.filter(user=info.context.user)

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    create_category = CreateCategory.Field()
    # verify_token = graphql_jwt.Verify.Field()
    # refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
