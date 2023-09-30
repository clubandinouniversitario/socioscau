from django.shortcuts import render
from django.views.generic import UpdateView, CreateView, DetailView, ListView, DeleteView
from django.views.generic.edit import FormMixin
from ..models import Member, Car, BaseNotice, ShortNotice, Friend
from ..forms import ShortNoticeForm, SendNoticeForm, ArrivedNoticeForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from dal import autocomplete
from django.utils import timezone as tz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

###############################################################################
#                                  Mixins                                     #
###############################################################################

class NoticeAuthMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.member in self.get_object().allowed_to_edit()

class NoticeSeeAuthMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.member in self.get_object().allowed_to_see()

###############################################################################
#                         Short Notice Autocompletes                          #
###############################################################################

class MemberAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Member.objects.none()

        qs = Member.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class CarsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Car.objects.none()

        qs = Car.objects.all()

        members = self.forwarded.get('participants', None)
        if members:
            qs_temp = Car.objects.none()
            for member_str in members:
                member = Member.objects.get(pk=member_str)
                qs_temp = qs_temp | qs.filter(member=member)
            qs = qs_temp
        else:
            qs = qs.filter(member=self.request.user.member)
        if self.q:
            qs = qs.filter(license_plate__istartswith=self.q)

        return qs

class FriendsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Friend.objects.none()

        qs = Friend.objects.all()

        members = self.forwarded.get('participants', None)
        if members:
            qs_temp = Friend.objects.none()
            for member_str in members:
                member = Member.objects.get(pk=member_str)
                qs_temp = qs_temp | qs.filter(member=member)
            qs = qs_temp
        else:
            qs = qs.filter(member=self.request.user.member)

        return qs

###############################################################################
#                              Short Notice CRUD                              #
###############################################################################

class CreateShortNoticeView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ShortNotice
    form_class = ShortNoticeForm
    template_name = 'avisos/shortnotice/create.html'
    success_message = 'Aviso creado correctamente. Recuerda que debes enviarlo para que se active.'
    pk = None

    def form_valid(self, form):
        form.instance.member = self.request.user.member
        item = form.save()
        self.pk = item.pk
        return super().form_valid(form)
    
    def get_initial(self):
        return {"participants": [self.request.user.member.pk]}

    def get_success_url(self):
         return reverse('avisos:detail_notice', kwargs={'pk': self.object.pk})

class DuplicateShortNoticeView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ShortNotice
    form_class = ShortNoticeForm
    template_name = 'avisos/shortnotice/create.html'
    success_message = 'Aviso creado correctamente. Recuerda que debes enviarlo para que se active.'
    original_notice = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        original_notice = ShortNotice.objects.get(pk=self.kwargs['pk'])
        context.update({
            'form': ShortNoticeForm(initial={
                'category': original_notice.category,
                'location': original_notice.location,
                'route': original_notice.route,
                'participants': original_notice.participants.all(),
                'friends': original_notice.friends.all(),
                'cau_contact': original_notice.cau_contact,
                'cars': original_notice.cars.all(),
                'parking_location': original_notice.parking_location,
                'other_transportation': original_notice.other_transportation,
                'description': original_notice.description,
            })})
        return context
    
    def form_valid(self, form):
        form.instance.member = self.request.user.member
        item = form.save()
        self.pk = item.pk
        return super().form_valid(form)

    def get_initial(self):
        return {"participants": [self.request.user.member.pk]}
    
    def get_success_url(self):
         return reverse('avisos:detail_notice', kwargs={'pk': self.object.pk})

class UpdateShortNoticeView(NoticeAuthMixin, SuccessMessageMixin, UpdateView):
    model = ShortNotice
    form_class = ShortNoticeForm
    template_name = 'avisos/shortnotice/edit.html'
    success_message = 'Aviso actualizado correctamente.'

    def get_success_url(self):
         return reverse('avisos:detail_notice', kwargs={'pk': self.object.pk})

class DeleteShortNoticeView(NoticeAuthMixin, SuccessMessageMixin, DeleteView):
    model = ShortNotice
    template_name = 'avisos/shortnotice/delete.html'
    success_message = 'Aviso eliminado correctamente.'

    def get_success_url(self):
         return reverse('avisos:myavisos')

class NoticesView(LoginRequiredMixin, ListView):
    model = BaseNotice
    template_name = 'avisos/index.html'
    title = ''

    class Meta:
        abstract = True

    def get_object(self):
        return Member.objects.get(user=self.request.user)

class AllNoticesView(NoticesView):
    title = 'Todos los Avisos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        default_page = 1
        avisos_full = BaseNotice.objects.exclude(status=0).exclude(status=5)
        paginator = Paginator(avisos_full, 6) # Show 5 notices per page
        page = self.request.GET.get('page', default_page)
        try:
          avisos_page = paginator.get_page(page)
        except PageNotAnInteger:
          # If page is not an integer, deliver first page.
          avisos_page = paginator.get_page(default_page)
        except EmptyPage:
          # If page is out of range (e.g. 9999), deliver last page of results.
          avisos_page = paginator.get_page(paginator.num_pages)
        context.update({'title': self.title, 'avisos_page': avisos_page})
        return context

class MyNoticesView(NoticesView):
    title = 'Mis Avisos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        default_page = 1
        avisos_full = BaseNotice.objects.filter(participants=self.request.user.member)
        paginator = Paginator(avisos_full, 6)
        page = self.request.GET.get('page', default_page)
        try:
          avisos_page = paginator.get_page(page)
        except PageNotAnInteger:
          # If page is not an integer, deliver first page.
          avisos_page = paginator.get_page(default_page)
        except EmptyPage:
          # If page is out of range (e.g. 9999), deliver last page of results.
          avisos_page = paginator.get_page(paginator.num_pages)
        context.update({'title': self.title, 'avisos_page': avisos_page})
        return context

class DetailNoticeView(NoticeSeeAuthMixin, FormMixin, DetailView):
    model = ShortNotice
    template_name = 'avisos/shortnotice/detail.html'
    
    def get(self, request, pk):
        return render(request, self.template_name, {'aviso': BaseNotice.objects.get(pk=pk)})

###############################################################################
#                            Short Notice Actions                             #
###############################################################################

class SendNoticeView(NoticeAuthMixin, SuccessMessageMixin, UpdateView):
    model = ShortNotice
    form_class = SendNoticeForm
    template_name = 'avisos/shortnotice/send.html'
    success_message = 'Aviso enviado correctamente.'

    def get_success_url(self):
         return reverse('avisos:detail_notice', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.sent_date = tz.now()
        form.instance.sent_by = self.request.user.member
        form.instance.sendto_caucontacts = True
        form.instance.sendto_participants = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SendNoticeForm()
        context.update({'aviso': ShortNotice.objects.get(pk=self.kwargs['pk'])})
        context.update({'form': SendNoticeForm(instance=self.object, initial={'sent_date': tz.now(), 'sent_by': self.request.user.member})})
        return context

class ArrivedNoticeView(NoticeAuthMixin, SuccessMessageMixin, UpdateView):
    model = ShortNotice
    form_class = ArrivedNoticeForm
    template_name = 'avisos/shortnotice/arrival.html'
    success_message = 'Llegada confirmada correctamente.'

    def get_success_url(self):
         return reverse('avisos:detail_notice', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.arrival_confirmation_date = tz.now()
        form.instance.arrival_confirmation_by = self.request.user.member
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ArrivedNoticeForm()
        context.update({'aviso': ShortNotice.objects.get(pk=self.kwargs['pk'])})
        context.update({'form': ArrivedNoticeForm(instance=self.object, initial={'arrival_confirmation_date': tz.now(), 'arrival_confirmation_by': self.request.user.member})})
        return context
