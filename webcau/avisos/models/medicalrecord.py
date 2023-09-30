from django.db.models.signals import post_save
from django.dispatch import receiver
from annoying.fields import AutoOneToOneField
from .base import *
from .member import Member

class MedicalRecord(BaseModel):
    member = AutoOneToOneField(Member, primary_key=True, on_delete=models.CASCADE)
    no_medical_record = models.BooleanField(default=False)
    sicknesses = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
   
    class Meta:
        verbose_name = "Ficha médica"
        verbose_name_plural = "Fichas médicas"
        ordering = ['member']
 
    def __str__(self):
        if self.no_medical_record:
            return str(self.member) + " - No tiene ficha médica"
        else:
            return str(self.member) + " - " + str(self.sicknesses)
    
    def pending(self):
        if self.no_medical_record:
            return False
        if self.sicknesses or self.medications or self.comments:
            return False
        return True

@receiver(post_save, sender=Member)
def create_member_medical(sender, instance, created, **kwargs):
    if created:
        MedicalRecord.objects.create(member=instance)

@receiver(post_save, sender=Member)
def save_member_medical(sender, instance, **kwargs):
    instance.medicalrecord.save()
