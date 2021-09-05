from rest_framework.views import APIView
from django.http import JsonResponse

class BudgetView(APIView):
    def get(self, request):
        return JsonResponse({ 'hello': 'get' })

    def put(self, request, id):
        return JsonResponse({ 'hello': f'update {id}' })

    def post(self, request):
        return JsonResponse({ 'hello': 'create' })
