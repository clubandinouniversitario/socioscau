from django.shortcuts import render
from django.views import View
from ..models import Member, Car, EmergencyContact, BaseNotice
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

class IndexView(LoginRequiredMixin, View):
    
    def get(self, request):
        return render(request, 'index.html', {'member': self.get_object(), 'cars': self.get_cars(), 'emergencycontacts': self.get_emergencycontacts(), 'active_notices': self.get_active_notices()})
    def get_object(self):
        return Member.objects.get(user=self.request.user)
    
    def get_cars(self):
        return Car.objects.filter(member=self.get_object())
    
    def get_emergencycontacts(self):
        return EmergencyContact.objects.filter(member=self.get_object())
    
    def get_active_notices(self):
        return [notice for notice in BaseNotice.objects.filter(Q(status=2) | Q(status=3)) if self.get_object() in notice.allowed_to_edit()]



class ObjectOwnerAuthMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().member == self.request.user.member

###############################################################################
#                         Mixin para modals con ajax                          #
###############################################################################
class AjaxTemplateMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.template_name = self.ajax_template_name
        return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)
