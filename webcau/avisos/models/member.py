from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .base import *
from .emergencycontact import EmergencyContact
from phonenumber_field.modelfields import PhoneNumberField


#   Member model. Pending: member status, image, signature, etc.
class Member(SoftDeletionModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True)
    first_surname = models.CharField(max_length=100)
    second_surname = models.CharField(max_length=100, blank=True)
    rut = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    use_middlename = models.BooleanField(default=False)
    use_second_surname = models.BooleanField(default=False)

    profile_image = models.ImageField(upload_to='profile_images', blank=True, validators =[file_size], default = 'default.png')

    class Meta:
        verbose_name = "Socio"
        verbose_name_plural = "Socios"
        ordering = ['name', 'first_surname']

    def get_absolute_url(self):
        return reverse('member-detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        if self.name and self.first_surname:
            middle = self.middlename if self.use_middlename else ""
            last = self.second_surname if self.use_second_surname else ""
            if middle == "":
                names = self.name
            else:
                names = self.name + " " + middle
            if last == "":
                surnames = self.first_surname
            else:
                surnames = self.first_surname + " " + last
            return names + " " + surnames
        return self.user.username

    def save(self, *args, **kwargs):
        if self.rut:
            exists = Member.objects.filter(rut=self.rut).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError("Ya existe un socio con este rut.")
        super().save(*args, **kwargs)

    @property
    def main_emergencycontact(self):
        return EmergencyContact.objects.filter(member=self, main_contact=True).first()

class ClubBoard(SoftDeletionModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(Member, blank=True, through='ClubBoardMember')

    class Meta:
        verbose_name = "Directiva"
        verbose_name_plural = "Directivas"
        ordering = ['name']

    def __str__(self):
        return self.name

class ClubBoardMember(SoftDeletionModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    clubboard = models.ForeignKey(ClubBoard, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    receivenotices = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Miembro de la directiva"
        verbose_name_plural = "Miembros de la directiva"
        ordering = ['clubboard', 'position']

    def __str__(self):
        return self.position + " en " + self.clubboard.name

class Committee(SoftDeletionModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(Member, blank=True, through='CommitteeMember')

    def __str__(self):
        return self.name

class CommitteeMember(SoftDeletionModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.position + " en " + self.committee.name

class EmailRecipient(SoftDeletionModel):
    email = models.EmailField(max_length=254)
    def __str__(self):
        return str(self.email)

class Friend(SoftDeletionModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True)
    first_surname = models.CharField(max_length=100)
    second_surname = models.CharField(max_length=100, blank=True)
    rut = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    
    emergencycontact_name = models.CharField(max_length=100)
    emergencycontact_phone = PhoneNumberField(null=True, blank=True)
    emergencycontact_email = models.EmailField(max_length=254, blank=True)
    emergencycontact_relationship = models.CharField(max_length=100, blank=True)

    sicknesses = models.CharField(max_length=100, blank=True)
    medications = models.CharField(max_length=100, blank=True)
    comments = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Amigo"
        verbose_name_plural = "Amigos"
        ordering = ['name', 'first_surname']

    def delete(self):
      self.member = None
      self.save()

    def __str__(self):
        return self.name + " " + self.middlename + " " + self.first_surname + " " + self.second_surname


