from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/guided/<str:public_id>/', consumers.GuidedQuizConsumer.as_asgi()),
]
