from .base import *

class GlobalSettings(BaseModel):
    logo_notice = models.ImageField(upload_to='avisos/logo_notice', null=True, blank=True)
    group_mail = models.EmailField(max_length=254, null=True, blank=True)
    not_authorized_image = models.ImageField(upload_to='avisos/not_authorized', null=True, blank=True)
    notice_arrival_mail_content = models.TextField(null=True, blank=True)
    notice_late_mail_content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Configuración global"
        verbose_name_plural = "Configuración global"

    def has_add_permission(self, request):
        # check if generally has add permission
        retVal = super().has_add_permission(request)
        # set add permission to False, if object already exists
        if retVal and models.ExampleModel.objects.exists():
            retVal = False
        return retVal
    
    def save(self, *args, **kwargs):
        if not self.pk and GlobalSettings.objects.exists():
        # if you'll not check for self.pk 
        # then error will also raised in update of exists model
            raise ValidationError('There is can be only one GlobalSettings instance')
        return super(GlobalSettings, self).save(*args, **kwargs)
