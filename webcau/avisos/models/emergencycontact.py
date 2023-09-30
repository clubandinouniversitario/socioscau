from django.db.models.signals import pre_save
from django.dispatch import receiver
from .base import *
from phonenumber_field.modelfields import PhoneNumberField


class EmergencyContact(SoftDeletionModel):
    member = models.ForeignKey('avisos.Member', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    main_contact = models.BooleanField(default=True)
    relationship = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['main_contact', 'member'], condition=models.Q(main_contact=True), name='unique_main_contact'),
        ]
        verbose_name = "Contacto de emergencia"
        verbose_name_plural = "Contactos de emergencia"
        ordering = ['member', 'name']

    def delete(self):
        self.main_contact = False
        return super().delete()

    def __str__(self):
        return str(self.name)

@receiver(pre_save, sender=EmergencyContact)
def set_main_contact(sender, instance, **kwargs):
    if instance.main_contact:
        EmergencyContact.objects.filter(main_contact=True, member=instance.member).update(main_contact=False)

