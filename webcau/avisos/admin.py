from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Car, MedicalRecord, NoticeCategory, ShortNotice, EmergencyContact, BaseNotice, GlobalSettings, Friend, ClubBoard, ClubBoardMember

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False
    max_num = 1

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    inlines = (MemberInline,)

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("__str__", "rut", "phone_number")
    search_fields = ("name", "middlename", "first_surname", "second_surname", "rut", "user__username")
admin.site.register(Car)
admin.site.register(MedicalRecord)
admin.site.register(NoticeCategory)
admin.site.register(ShortNotice)
admin.site.register(EmergencyContact)
admin.site.register(GlobalSettings)
admin.site.register(Friend)
admin.site.register(ClubBoard)
admin.site.register(ClubBoardMember)

