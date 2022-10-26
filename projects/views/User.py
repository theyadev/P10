from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

class SignupView(APIView):
    def post(self, request):
        if not 'username' in request.data or not 'password' in request.data:
            return Response(status=400, data={'error': 'Missing required fields. (username, password)'})
        if User.objects.filter(username=request.data['username']).exists():
            return Response(status=400, data={'error': 'Username already exists.'})
        user = User.objects.create_user(
            username=request.data['username'], password=request.data['password'])
        return Response({'id': user.id})