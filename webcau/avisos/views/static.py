from django.shortcuts import render
from django.views import View
from django.views.generic import UpdateView, CreateView, DeleteView
from ..models import Member, MedicalRecord, Car, EmergencyContact, Friend
from ..forms import MemberForm, MedicalForm, CarForm, EmergencyContactForm, FriendForm
from ..views.base import ObjectOwnerAuthMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

###############################################################################
#                                    Member                                   #
###############################################################################

class UpdateAccountView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'account/settings.html'
    success_url = reverse_lazy('account_data')
    success_message = 'Datos actualizados correctamente'

    def get_object(self):
        return Member.objects.get(user=self.request.user)

###############################################################################
#                                   Medical                                   #
###############################################################################

class UpdateMedicalView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MedicalRecord
    form_class = MedicalForm
    template_name = 'medical/settings.html'
    success_url = reverse_lazy('medical_data')
    success_message = 'Datos actualizados correctamente'

    def get_object(self):
        return MedicalRecord.objects.get(member=self.request.user.member)

###############################################################################
#                                     Car                                     #
###############################################################################

class CarsView(LoginRequiredMixin, View):
    template_name = 'car/index.html'

    def get(self, request):
        return render(request, self.template_name, {'cars': Car.objects.filter(member=request.user.member)})

class UpdateCarView(SuccessMessageMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'car/edit.html'
    success_url = reverse_lazy('cars_data')
    success_message = 'Datos actualizados correctamente'

class CreateCarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'car/create.html'
    success_url = reverse_lazy('cars_data')
    success_message = 'Vehículo creado correctamente'

    def form_valid(self, form):
        form.instance.member = self.request.user.member
        return super().form_valid(form)

class DeleteCarView(DeleteView):
    model = Car
    success_url = reverse_lazy('cars_data')

###############################################################################
#                            Emergency Contact                                #
###############################################################################

class EmergencyContactsView(LoginRequiredMixin, View):
    template_name = 'emergencycontact/index.html'

    def get(self, request):
        return render(request, self.template_name, {'emergencycontacts': EmergencyContact.objects.filter(member=request.user.member).order_by('-main_contact')})

class UpdateEmergencyContactView(SuccessMessageMixin, UpdateView):
    model = EmergencyContact
    form_class = EmergencyContactForm
    template_name = 'emergencycontact/edit.html'
    success_url = reverse_lazy('emergencycontacts_data')
    success_message = 'Datos actualizados correctamente'

class CreateEmergencyContactView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = EmergencyContact
    form_class = EmergencyContactForm
    template_name = 'emergencycontact/create.html'
    success_url = reverse_lazy('emergencycontacts_data')
    success_message = 'Contacto creado correctamente'

    def form_valid(self, form):
        form.instance.member = self.request.user.member
        return super().form_valid(form)

class DeleteEmergencyContactView(ObjectOwnerAuthMixin, DeleteView):
    model = EmergencyContact
    success_url = reverse_lazy('emergencycontacts_data')


###############################################################################
#                                     Friend                                     #
###############################################################################

class FriendsView(LoginRequiredMixin, View):
    template_name = 'friend/index.html'

    def get(self, request):
        return render(request, self.template_name, {'friends': Friend.objects.filter(member=request.user.member)})

class UpdateFriendView(SuccessMessageMixin, UpdateView):
    model = Friend
    form_class = FriendForm
    template_name = 'friend/edit.html'
    success_url = reverse_lazy('friends_data')
    success_message = 'Datos actualizados correctamente'

class CreateFriendView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Friend
    form_class = FriendForm
    template_name = 'friend/create.html'
    success_url = reverse_lazy('friends_data')
    success_message = 'Amigo creado correctamente'

    def form_valid(self, form):
        form.instance.member = self.request.user.member
        return super().form_valid(form)

class DeleteFriendView(DeleteView):
    model = Friend
    success_url = reverse_lazy('friends_data')
