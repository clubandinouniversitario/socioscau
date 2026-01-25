from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Member, Car, MedicalRecord, NoticeCategory, ShortNotice, EmergencyContact, BaseNotice, GlobalSettings, Friend, ClubBoard, ClubBoardMember


class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False
    max_num = 1

class CustomUserAdmin(UserAdmin):
    inlines = (MemberInline,)



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Member)
admin.site.register(Car)
admin.site.register(MedicalRecord)
admin.site.register(NoticeCategory)
admin.site.register(ShortNotice)
admin.site.register(EmergencyContact)
admin.site.register(GlobalSettings)
admin.site.register(Friend)
admin.site.register(ClubBoard)
admin.site.register(ClubBoardMember)

