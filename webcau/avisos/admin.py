from django.contrib import admin
from .models import Member, Car, MedicalRecord, NoticeCategory, ShortNotice, EmergencyContact, BaseNotice, GlobalSettings, Friend, ClubBoard, ClubBoardMember

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

