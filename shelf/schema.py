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
            'spent'
        )

    spent = graphene.Int()
    def resolve_spent(instance, info):
        return instance.spent()

    progress = graphene.Int()
    def resolve_progress(instance, info):
        return instance.progress()


class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)

    @login_required
    def resolve_all_categories(self, info):
        return Category.objects.filter(user_id=info.context.user.id)

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    # verify_token = graphql_jwt.Verify.Field()
    # refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
