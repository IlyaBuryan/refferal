
######## POST Запрос на отправку проврочного кода. Принимает и валидизирует номер телефона.
######## Создает в базе пользователя с id и check_code

Запрос:
api/v1/user_auth/ [name='user_auth']
http://89.108.71.100:8004/api/v1/user_auth/

Формат:
{
    "phone": "79099654555"
}

######## POST Запрос проверки кода и отправки токена. Принимает номер телефона и проверочный код.
######## В случае успеха создает у юзера кникальный self_invite_code.

Запрос:
api/v1/check_code/ [name='check_code']

Формат:
{
    "phone": "79099654555",
    "check_code": "7431"
}

######## POST Запрос изменения чужого other_invite_code. Принимает и валидизирует invite_code + token авторизации.
######## В случае успеха записывает у юзера other_invite_code (код приглашение другого пользователя)

Запрос:
api/v1/user_update/<int:pk>/ [name='user_update']

Формат:
{
    "other_invite_code": "YoYTyU"
}


######## GET Запрос на вывод данных пользователя по id + всех связанных с ним по его self_invite_code юзерами.

Запрос:
api/v1/user_view/<int:user_pk>/ [name='user_view']


######## Доступ к документации API:
http://89.108.71.100:8004/swagger/
http://89.108.71.100:8004/swagger.json
http://89.108.71.100:8004/redoc/
