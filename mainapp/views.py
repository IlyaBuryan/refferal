import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

from .serializers import UserSerializer, UserUpdateSerializer
from .models import User
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_view(request, user_pk):
    if request.method == 'GET':
        user = User.objects.filter(pk=user_pk).values_list('id',
                                                           'phone',
                                                           'self_invite_code',
                                                           'other_invite_code')
        try:
            self_invite_code = User.objects.filter(pk=user_pk).first().self_invite_code
        except:
            return JsonResponse({'result': 'No such user'})

        if self_invite_code:
            other_users = User.objects.filter(other_invite_code=self_invite_code).values_list('phone', flat=True)
        else:
            other_users = []

        return JsonResponse({
            'current_user': list(user),
            'invited_users_numbers': list(other_users),
        })


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['POST'])
def auth_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            check_code = User.generate_check_code()
            serializer.validated_data['check_code'] = check_code
            time.sleep(2)  # sended check code to the phone
            serializer.save()
            return JsonResponse({'result': f'{check_code} Check code sent to the phone'})
        else:
            return JsonResponse({'result': serializer.errors})


@api_view(['POST'])
def check_code(request):
    phone = request.data.get('phone', None)
    code = request.data.get('check_code', None)
    if phone and code:
        try:
            user = User.objects.get(phone=phone, check_code=code)
            user.self_invite_code = User.generate_invite()
            user.save()
        except:
            return JsonResponse({'result': 'Phone number or code is not valid'})
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key})
    else:
        return JsonResponse({'result': 'Phone number or code has not been sent'})
