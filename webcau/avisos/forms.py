from django import forms
from dal import autocomplete
from django.core.mail import send_mail

from .models import Member, MedicalRecord, Car, EmergencyContact, ShortNotice, Friend, NoticeCategory
from phonenumber_field.widgets import PhoneNumberPrefixWidget

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('profile_image', 'user', 'name', 'middlename', 'first_surname', 'second_surname', 'rut', 'birth_date', 'phone_number', 'use_middlename', 'use_second_surname' )
        widgets = {
            'user': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'middlename': forms.TextInput(attrs={'class': 'form-control'}),
            'first_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'second_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(
                format= '%Y-%m-%d',
                attrs={
                    'type': 'date', 
                    'class': 'form-control',
                    }
                ),
            'phone_number': PhoneNumberPrefixWidget(initial='CL', attrs={'class': 'form-control'}),
            'use_middlename': forms.CheckboxInput(attrs={'class': 'form-check-inline'}),
            'use_second_surname': forms.CheckboxInput(attrs={'class': 'form-check-inline'}),
            'profile_image': forms.FileInput(
                attrs={
                    'class': 'form-control form-control'
                }),
        }
        labels = {
            'name': 'Nombre',
            'middlename': 'Segundo Nombre',
            'first_surname': 'Apellido Paterno',
            'second_surname': 'Apellido Materno',
            'rut': 'RUT',
            'birth_date': 'Fecha de Nacimiento',
            'phone_number': 'Número de Teléfono',
            'use_middlename': 'Usar Segundo Nombre',
            'use_second_surname': 'Usar Apellido Materno',
            'profile_image': 'Foto de Perfil (max 2MB)',
        }
        required = {
          'name',
          'first_surname',
          'phone_number',
        }
        help_texts = {
          'use_middlename': 'Si el segundo nombre es requerido, marque esta opción',
          'use_second_surname': 'Si el apellido materno es requerido, marque esta opción',
        }
        exclude = ['user']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

class MedicalForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ('no_medical_record', 'sicknesses', 'medications', 'comments')
        widgets = {
            'member': forms.HiddenInput(),
            'no_medical_record': forms.CheckboxInput(attrs={'class': 'form-check-inline'}),
            'sicknesses': forms.TextInput(attrs={'class': 'form-control'}),
            'medications': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'no_medical_record': 'No tengo nada que ingresar.',
            'sicknesses': 'Enfermedades',
            'medications': 'Medicamentos',
            'comments': 'Comentarios',
        }
        exclude = ['member']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

class FriendForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True
    class Meta:
        model = Friend
        fields = ('member', 'name', 'middlename', 'first_surname', 'second_surname', 'rut', 'birth_date', 'phone_number', 'email', 'emergencycontact_name', 'emergencycontact_phone', 'emergencycontact_email', 'emergencycontact_relationship', 'sicknesses', 'medications', 'comments')
        widgets = {
            'member': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'middlename': forms.TextInput(attrs={'class': 'form-control'}),
            'first_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'second_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': PhoneNumberPrefixWidget(initial='CL', attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'emergencycontact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergencycontact_phone': PhoneNumberPrefixWidget(initial='CL', attrs={'class': 'form-control'}),
            'emergencycontact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'emergencycontact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'sicknesses': forms.TextInput(attrs={'class': 'form-control'}),
            'medications': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre',
            'middlename': 'Segundo Nombre',
            'first_surname': 'Apellido Paterno',
            'second_surname': 'Apellido Materno',
            'rut': 'RUT',
            'birth_date': 'Fecha de Nacimiento',
            'phone_number': 'Número de Teléfono',
            'email': 'Correo Electrónico',
            'emergencycontact_name': 'Nombre de Contacto de Emergencia',
            'emergencycontact_phone': 'Teléfono de Contacto de Emergencia',
            'emergencycontact_email': 'Correo Electrónico de Contacto de Emergencia',
            'emergencycontact_relationship': 'Parentesco de Contacto de Emergencia',
            'sicknesses': 'Enfermedades',
            'medications': 'Medicamentos',
            'comments': 'Comentarios (salud)',
        }
        required = {
          'name',
          'first_surname',
          'phone_number',
          'emergencycontact_name',
          'emergencycontact_phone',
        }
        exclude = ['member']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ('name', 'phone_number', 'email', 'relationship', 'main_contact')
        widgets = {
            'member': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': PhoneNumberPrefixWidget(initial='CL', attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'main_contact': forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre Completo',
            'phone_number': 'Número de Teléfono',
            'email': 'Correo Electrónico',
            'main_contact': '¿Es tu contacto predeterminado?',
            'relationship': 'Relación / Grado de Parentesco (Papá, Mamá, Tío, Tía, etc.)',
        }
        help_texts = {
          'main_contact': 'Si es tu contacto predeterminado, marca esta opción',
        }
        required = {
          'name',
          'phone_number',
        }
        exclude = ['member']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('alias', 'brand', 'model', 'year', 'license_plate', 'color')
        widgets = {
            'member': forms.HiddenInput(),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'alias': 'Alias (para identificarlo: Mi Auto, Auto de mi Hermana, etc.)',
            'brand': 'Marca',
            'model': 'Modelo',
            'year': 'Año',
            'license_plate': 'Patente',
            'color': 'Color',
        }
        exclude = ['member']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

class ShortNoticeForm(forms.ModelForm):
    category = forms.ModelChoiceField(
      queryset=NoticeCategory.objects.order_by('priority'), 
      widget=forms.Select(attrs={'class': 'form-control'}), 
      label='Categoría', 
      required=True,
      help_text='Categoría de la actividad a realizar',
      )
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

      for field in self.Meta.required:
        self.fields[field].required = True

    class Meta:
        model = ShortNotice
        fields = ('category', 'location', 'route', 'start_date', 'max_end_date', 'participants', 'friends', 'cau_contact', 'cars', 'parking_location', 'other_transportation', 'description')
        widgets = {
            'location': forms.TextInput(
              attrs={
                'class': 'form-control',
                'required': True,
                },
              ),
            'route': forms.TextInput(
              attrs={'class': 'form-control'},
              ),
            'start_date': forms.DateTimeInput(
                format= '%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local', 
                    'class': 'form-control',
                    'required': True,
                    },
                ),
            'max_end_date': forms.DateTimeInput(
                format= '%Y-%m-%dT%H:%M',  
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    },
                ),
            'cau_contact': autocomplete.ModelSelect2(
                url='avisos:member_autocomplete',
                attrs={
                    'data-placeholder': 'Buscar'
                    },
                ),
            # Initial value: current member
            'participants': autocomplete.ModelSelect2Multiple(
                url='avisos:member_autocomplete',
                attrs={
                    'data-placeholder': 'Buscar'
                    },
                ),
            'cars': autocomplete.ModelSelect2Multiple(
                url='avisos:cars_autocomplete',
                forward=['participants'],
                attrs={
                    'data-placeholder': 'Buscar'
                    },
                ),
            'parking_location': forms.TextInput(attrs={'class': 'form-control'}),
            'other_transportation': forms.TextInput(attrs={'class': 'form-control'}),
            'friends': autocomplete.ModelSelect2Multiple(
                url='avisos:friends_autocomplete',
                forward=['participants'],
                attrs={
                    'data-placeholder': 'Buscar'
                    },
                ),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        required = {
          'category',
          'location',
          'route',
          'start_date',
          'max_end_date',
          'participants',
        }
        help_texts = {
          'location': "Lugar donde se realizará la actividad",
          'route': "Ruta o equivalente donde se realizará la actividad",
          'start_date': "Fecha y hora de inicio de la actividad. Recomendamos no cambiar esta fecha una vez que publicas el aviso, ya que el sistema no funcionará correctamente.",
          'max_end_date': "Fecha y hora de fin de la actividad. Recuerda que debes tener señal para notificar tu llegada antes de esta hora. Si no hay notificación al superar el plazo, se activarán las alertas del club. Recomendamos no cambiar esta fecha una vez que publicas el aviso, ya que el sistema no funcionará correctamente.",
          'cau_contact': "Socio fuera de la cordada responsable de la actividad desde un lugar con señal para poder activar protocolos de emergencia en caso de ser necesario.",
          'participants': "Socios que participarán en la actividad",
          'cars': "Vehículos que se usarán para dirigirse a la actividad. Debes agregarlos previamente en la cuenta de alguien que participe en la salida, en 'amigos'.",
          'parking_location': "Lugar donde se guardarán los vehículos que se usen para la actividad.",
          'other_transportation': "Detallar cualquier otra forma de transporte que se usará para la actividad (autos no agregados, traslado por un familiar, transporte público, etc) ",
          'friends': "Personas externas al CAU que participarán en la actividad. Debes agregarlas previamente en la cuenta de alguien que participe en la salida, en 'amigos'.",
          'description': "Descripción de la actividad. Cualquier información que complemente la información ya ingresada.",
        }
      
        labels = {
            'location': 'Lugar',
            'category': 'Categoría',
            'route': 'Ruta(s)',
            'start_date': 'Fecha de Inicio',
            'max_end_date': 'Plazo Máximo de Llegada',
            'participants': 'Miembros de la cordada',
            'friends': 'Amigos externos al CAU',
            'cau_contact': 'Contacto CAU',
            'cars': 'Vehículos',
            'parking_location': 'Lugar de estacionamiento',
            'other_transportation': 'Otros medios de transporte',
            'description': 'Comentarios',
        }
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

class SendNoticeForm(forms.ModelForm):
    sendto_caucontacts_fake = forms.BooleanField(required=False, label='Enviar a contactos CAU', widget=forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox', 'disabled': True, 'checked': True}))
    sendto_participants_fake = forms.BooleanField(required=False, label='Enviar a cordada', widget=forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox', 'disabled': True, 'checked': True}))
    sendto_board = forms.BooleanField(required=False, label='Enviar a directiva', widget=forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox', 'disabled': False, 'checked': True}))
    sendto_emergencycontacts = forms.BooleanField(required=False, label='Enviar a contactos de emergencia', widget=forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox', 'checked': True}))
    sendto_caumembers = forms.BooleanField(required=False, label='Enviar a Google Group CAU', widget=forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox', 'checked': True}))
    sendto_otheremails = forms.CharField(required=False, label='Incluir otros correos electrónicos (sepáralos con comas ",")', widget=forms.TextInput(attrs={'class': 'form-control email-addresses'}))
    mail_body = forms.CharField(required=False, label='Mensaje', widget=forms.Textarea(attrs={'class': 'form-control'}))
    include_pdf = forms.BooleanField(required=False, label='Incluir PDF como adjunto', widget=forms.CheckboxInput(attrs={'class': 'form-check-inline big-checkbox', 'checked': True}))

    sendto_caucontacts = forms.BooleanField(required=False, initial=True, label='Enviar a contactos CAU', widget=forms.HiddenInput())
    sendto_participants = forms.BooleanField(required=False, initial=True, label='Enviar a cordada', widget=forms.HiddenInput())

    class Meta:
        model = ShortNotice
        fields = ()
        widgets = {
            'sent_date': forms.HiddenInput(),
            'sent_by': forms.HiddenInput(),
        }
        exclude = ['sent_date', 'sent_by']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())

    def save(self, commit=True):
        instance = super(SendNoticeForm, self).save(commit = False)
        instance.email_recipients.clear()
        if self.cleaned_data['sendto_caucontacts']:
            instance.include_caucontacts()
        if self.cleaned_data['sendto_participants']:
            instance.include_participants()
        if self.cleaned_data['sendto_board']:
            instance.include_board()
        if self.cleaned_data['sendto_emergencycontacts']:
            instance.include_emergencycontacts()
        if self.cleaned_data['sendto_caumembers']:
            instance.include_caumembers()
        
        list_of_mails = self.cleaned_data['sendto_otheremails'].strip('[]').split(',')
        for email in list_of_mails:
            email = email.replace('"', '')
            instance.include_email(email, False)

        mail_content = self.cleaned_data['mail_body']

        if commit:
            instance.include_pdf = self.cleaned_data['include_pdf']
            instance.save()
            instance.publish_notice(mail_content = mail_content)

        return instance

class ArrivedNoticeForm(forms.ModelForm):
    class Meta:
        model = ShortNotice
        fields = ('arrival_message',)
        widgets = {
            'arrival_message': forms.Textarea(attrs={'class': 'form-control'}),
            'arrival_confirmation_date': forms.HiddenInput(),
            'arrival_confirmation_by': forms.HiddenInput(),
        }
        help_texts = {
            'arrival_message': 'Mensaje que se enviará en el correo de confirmación de llegada.',
        }
        labels = {
            'arrival_message': 'Mensaje de confirmación de llegada',
        }
        exclude = ['arrival_confirmation_date', 'arrival_confirmation_by']
        action = forms.CharField(max_length=60, widget=forms.HiddenInput())
    
    def save(self, commit=True):
        instance = super(ArrivedNoticeForm, self).save(commit = False)

        if commit:
            instance.save()
            instance.notify_arrival()

        return instance
