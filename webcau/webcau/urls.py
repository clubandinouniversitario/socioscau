from django.contrib import admin
from django.urls import include, path
from avisos.views.base import IndexView
from avisos.views.account import UpdateAccountView, UpdateMedicalView, CarsView, CreateCarView, UpdateCarView, DeleteCarView, EmergencyContactsView, CreateEmergencyContactView, UpdateEmergencyContactView, DeleteEmergencyContactView, FriendsView, CreateFriendView, UpdateFriendView, DeleteFriendView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('acceso/', include('django.contrib.auth.urls')),
    path('', include('avisos.urls')),
    path('', IndexView.as_view(), name='index'),
    path('cuenta/panel', UpdateAccountView.as_view(), name='account_data'),
    path('cuenta/salud/', UpdateMedicalView.as_view(), name='medical_data'),
    path('cuenta/vehiculos/', CarsView.as_view(), name='cars_data'),
    path('cuenta/vehiculos/nuevo', CreateCarView.as_view(), name='new_car'),
    path('cuenta/vehiculos/<int:pk>/', UpdateCarView.as_view(), name='edit_car'),
    path('cuenta/vehiculos/<int:pk>/eliminar', DeleteCarView.as_view(), name='delete_car'),
    path('cuenta/contactos/', EmergencyContactsView.as_view(), name='emergencycontacts_data'),
    path('cuenta/contactos/nuevo', CreateEmergencyContactView.as_view(), name='new_emergencycontact'),
    path('cuenta/contactos/<int:pk>/', UpdateEmergencyContactView.as_view(), name='edit_emergencycontact'),
    path('cuenta/contactos/<int:pk>/eliminar', DeleteEmergencyContactView.as_view(), name='delete_emergencycontact'),
    path('cuenta/amigos/', FriendsView.as_view(), name='friends_data'),
    path('cuenta/amigos/nuevo', CreateFriendView.as_view(), name='new_friend'),
    path('cuenta/amigos/<int:pk>/', UpdateFriendView.as_view(), name='edit_friend'),
    path('cuenta/amigos/<int:pk>/eliminar', DeleteFriendView.as_view(), name='delete_friend'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
