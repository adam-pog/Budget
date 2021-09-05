from rest_framework.views import APIView
from django.http import JsonResponse

class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()

        return JsonResponse({})
