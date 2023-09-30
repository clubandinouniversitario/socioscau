from django.urls import path
from . import views
from avisos.views.notices import MyNoticesView, AllNoticesView, DetailNoticeView, CreateShortNoticeView, UpdateShortNoticeView, MemberAutocomplete, CarsAutocomplete, FriendsAutocomplete, SendNoticeView, ArrivedNoticeView, DeleteShortNoticeView, DuplicateShortNoticeView
from avisos.views.pdf_gen import PDFNoticeView
from avisos.views.base import IndexView

app_name = 'avisos'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('avisos/', AllNoticesView.as_view(), name='avisos'),
    path('avisos/misavisos/', MyNoticesView.as_view(), name='myavisos'),
    path('avisos/nuevo_rapido/', CreateShortNoticeView.as_view(), name='new_shortnotice'),
    path('avisos/nuevo_rapido/<int:pk>/', DuplicateShortNoticeView.as_view(), name='duplicate_shortnotice'),
    path('avisos/<int:pk>/editar', UpdateShortNoticeView.as_view(), name='edit_shortnotice'),
    path('avisos/<int:pk>/enviar', SendNoticeView.as_view(), name='send_shortnotice'),
    path('avisos/<int:pk>/eliminar', DeleteShortNoticeView.as_view(), name='delete_shortnotice'),
    path('avisos/<int:pk>/llegada', ArrivedNoticeView.as_view(), name='arrive_shortnotice'),
    path('avisos/<int:pk>/', DetailNoticeView.as_view(), name='detail_notice'),
    path('avisos/member_autocomplete/', MemberAutocomplete.as_view(), name='member_autocomplete'),
    path('avisos/cars_autocomplete/', CarsAutocomplete.as_view(), name='cars_autocomplete'),
    path('avisos/friends_autocomplete/', FriendsAutocomplete.as_view(), name='friends_autocomplete'),
    path('avisos/<int:pk>/pdf', views.PDFNoticeView, name='pdf_notice'),
]
