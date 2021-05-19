import time

from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse

from .serializers import UserSerializer, UserUpdateSerializer, UserLoginSerializer
from .models import User, UserLogin
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['pk'])
        token_user = str(Token.objects.get(user=user))
        token_request = request.META.get("HTTP_AUTHORIZATION").split()[1]
        if token_user != token_request:
            raise ValidationError(f'This is not your profile')
        elif user.other_invite_code:
            raise ValidationError('Code already exists')
        elif request.data['other_invite_code'] == user.self_invite_code:
            raise ValidationError('This code is yours')
        return super().update(request, *args, **kwargs)


@api_view(['POST'])
def auth_user(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            # Check and delete previous check data
            phone = request.data.get('phone', None)
            current_code = UserLogin.objects.filter(phone=phone).first()
            if current_code is not None:
                current_code.delete()
            # Create a new check information
            check_code = UserLogin.generate_check_code()
            serializer.validated_data['check_code'] = check_code
            serializer.save()
            time.sleep(2)  # sended check code to the phone
            return JsonResponse({'result': f'{check_code} Check code sent to the phone'})
        else:
            return JsonResponse({'result': serializer.errors})


@api_view(['POST'])
def check_code(request):
    phone = request.data.get('phone', None)
    code = request.data.get('check_code', None)
    if phone and code:
        try:
            user_login = UserLogin.objects.get(phone=phone, check_code=code)
            user = User.objects.filter(phone=phone).first()
            if user is None:
                cur_user = User.objects.create(phone=phone, self_invite_code=User.generate_invite())
                cur_user.save()
                token = Token.objects.get(user=cur_user)
            else:
                token = Token.objects.get(user=user)
            user_login.delete()
        except:
            return JsonResponse({'result': 'Phone number or code is not valid'})
        return JsonResponse({'token': token.key})
    else:
        return JsonResponse({'result': 'Phone number or code has not been sent'})
