import graphene
from graphene_django import DjangoObjectType

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
        fields = ('id', 'label', 'monthly_amount', 'user', 'created', 'modified')

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    category_by_label = graphene.Field(CategoryType, label=graphene.String(required=True))

    def resolve_all_users(root, info):
        # We can easily optimize query count in the resolve method
        return User.objects.all()

    def resolve_category_by_label(root, info, label):
        try:
            return Category.objects.get(label=label)
        except Category.DoesNotExist:
            return None

schema = graphene.Schema(query=Query)
