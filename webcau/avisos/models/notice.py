from datetime import timedelta
from django.db.models.signals import post_save
import celery
from django.dispatch import receiver
from django.utils import timezone as tz
from django.core.mail import send_mail, EmailMessage
from .base import *
from .member import Member, EmailRecipient, ClubBoard, Friend, ClubBoardMember
from .car import Car
import io
from .global_settings import *
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable, ListFlowable, ListItem, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def datetime_now_rounder():
    if tz.now().hour == 22:
        return tz.now().replace(hour=23, minute=0, second=0, microsecond=0)
    elif tz.now().hour == 23:
        temp_time = tz.now() + timedelta(days=1)
        return temp_time.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return tz.now().replace(hour=tz.now().hour + 1, minute=0, second=0, microsecond=0)
    
class NoticeCategory(SoftDeletionModel):
  name = models.CharField(max_length=100)
  priority = models.IntegerField(default=0)
  
  class Meta:
    verbose_name = "Categoría de aviso"
    verbose_name_plural = "Categorías de avisos"
    ordering = ['priority']
  
  def __str__(self):
      return self.name

class BaseNotice(SoftDeletionModel):
    location = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    DRAFT = 0
    PUBLISHED = 1
    ACTIVE = 2
    LATE = 3
    ARRIVED = 4
    CANCELLED = 5
    STATUS_CHOICES = (
        (DRAFT, 'Borrador'),
        (PUBLISHED, 'Publicado'),
        (ACTIVE, 'Activo'),
        (LATE, 'Retrasado'),
        (ARRIVED, 'Llegado'),
        (CANCELLED, 'Cancelado'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    category = models.ForeignKey(NoticeCategory, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime_now_rounder, blank=True)
    max_end_date = models.DateTimeField(default=datetime_now_rounder, blank=True)
    participants = models.ManyToManyField(Member, blank=True)
    friends = models.ManyToManyField(Friend, blank=True)
    cars = models.ManyToManyField(Car, blank=True)
    parking_location = models.CharField(max_length=100, blank=True)
    cau_contact = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="cau_contact", blank=True, null=True)
    other_transportation = models.CharField(max_length=100, blank=True, null=True)

    email_recipients = models.ManyToManyField(EmailRecipient, blank=True, related_name="email_recipients")
    email_late_alert_recipients = models.ManyToManyField(EmailRecipient, blank=True, related_name="email_late_alert_recipients")
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="sent_by", blank=True, null=True)
    arrival_confirmation_date = models.DateTimeField(null=True, blank=True)
    arrival_confirmation_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="arrival_confirmation_by", blank=True, null=True)
    include_pdf = models.BooleanField(default=True)

    arrival_message = models.TextField(blank=True, null=True)
    arrival_result = models.TextField(blank=True, null=True)
    arrival_conditions = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        ordering = ['-start_date']

    def __str__(self):
        return str(self.start_date.date()) + " - " + self.category.name + ": " + self.location + " - " + self.route

    def participants_tostring(self):
        return ", ".join([", ".join([str(member) for member in self.participants.all()]), ", ".join([str(friend) for friend in self.friends.all()])])

    def start_celery_task(self, number):
        if number == 1:
            print("vamos a empezar la espera hasta start_date" + str(self.start_date))
            celery.current_app.send_task(name='avisos.tasks.wait_for_start_time', args=(self.id,), eta=self.start_date)
            print("ya hemos empezado la espera hasta start_date"+ str(self.start_date))
        elif number == 2:
            print("vamos a empezar la espera hasta fin máximo")
            celery.current_app.send_task(name='avisos.tasks.wait_for_max_end_time', args=(self.id,), eta=self.max_end_date)
            print("ya hemos empezado la espera hasta fin máximo")

    def allowed_to_see(self):
        if self.status == self.DRAFT:
            return list(self.participants.all()) + [self.cau_contact]
        else:
          return Member.objects.all()

    def allowed_to_edit(self):
        return list(self.participants.all()) + [self.cau_contact]

    def include_email(self, email, late_alert=False):
        if email == "" or email is None:
            return
        if EmailRecipient.objects.filter(email=email).exists():
            self.email_recipients.add(EmailRecipient.objects.filter(email=email).first())
            if late_alert:
                self.email_late_alert_recipients.add(EmailRecipient.objects.filter(email=email).first())
        else:
            self.email_recipients.add(EmailRecipient.objects.create(email=email))
            if late_alert:
                self.email_late_alert_recipients.add(EmailRecipient.objects.create(email=email))

    def include_caucontacts(self):
        if self.cau_contact:
            self.include_email(self.cau_contact.user.email, True)

    def include_participants(self):
        for member in self.participants.all():
            self.include_email(member.user.email, True)
        for friend in self.friends.all():
            self.include_email(friend.email, True)

    def include_board(self):
        if ClubBoard.objects.count() > 0:
            for member in ClubBoard.objects.first().members.all():
                # check if clubboardmembers that have this member receivenotices
                clubboardmember = ClubBoardMember.objects.filter(member=member).first()
                if clubboardmember and clubboardmember.receivenotices:
                    self.include_email(member.user.email, True)
    
    def include_emergencycontacts(self):
        for member in self.participants.all():
            if member.main_emergencycontact:
                self.include_email(member.main_emergencycontact.email, False)
        for friend in self.friends.all():
            if friend.emergencycontact_email:
                self.include_email(friend.emergencycontact_email, False)

    def include_caumembers(self):
      if GlobalSettings.objects.count() > 0:
        if GlobalSettings.objects.first().group_mail:
          self.include_email(GlobalSettings.objects.first().group_mail, False)

    def publish_notice(self, mail_content=None):
        # Crear Validadores
        celery.current_app.send_task(name='avisos.tasks.enqueue_mail', args=(self.id, True, False, False, False, mail_content))
        if tz.now() >= self.max_end_date:
            # Confirmar que queremos hacer esto
            self.late_notice()
        elif tz.now() >= self.start_date:
            self.activate_notice()
        else:
            self.start_celery_task(1)
            self.status = self.PUBLISHED
            self.save()
    
    def activate_notice(self):
        if tz.now() >= self.max_end_date:
            # Confirmar que queremos hacer esto
            self.late_notice()
        elif tz.now() >= self.start_date:
            self.status = self.ACTIVE
            self.save()
            self.start_celery_task(2)

    def late_notice(self):
        if tz.now() >= self.max_end_date and self.status == self.ACTIVE:
            self.status = self.LATE
            self.save()
            celery.current_app.send_task(name='avisos.tasks.enqueue_mail', args=(self.id, False, False, True, False, None))
        elif tz.now() >= self.max_end_date:
            self.status = self.LATE
            self.save()

    def notify_arrival(self):
        if self.status != self.ARRIVED:
            self.status = self.ARRIVED
            self.save()
            celery.current_app.send_task(name='avisos.tasks.enqueue_mail', args=(self.id, False, True, False, False, None))


    def cancel_notice(self):
        self.status = self.CANCELLED
        self.save()
        # celery.current_app.send_task(name='avisos.tasks.enqueue_mail', args=(self.id, False, False, False, True, None))

    
    ###############################################################################
    #                                  PDF Files                                  #
    ###############################################################################
    def createPDF(self, buff, pdf_name):
        doc = SimpleDocTemplate(buff, title=pdf_name, pagesize=letter, rightMargin=24, leftMargin=24, topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='main_title', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, leading=14))
        styles.add(ParagraphStyle(name='subtitles', fontName='Helvetica-Bold', fontSize=11, leading=11))
        styles.add(ParagraphStyle(name='notice_bold', fontName='Helvetica-Bold', fontSize=10, leading=10))
        styles.add(ParagraphStyle(name='notice', fontName='Helvetica', fontSize=10, leading=10))
        styles.add(ParagraphStyle(name='final_content', fontName='Helvetica', fontSize=9, leading=9))
        styles.add(ParagraphStyle(name='final_content_bold', fontName='Helvetica-Bold', fontSize=9, leading=9))
        styles.add(ParagraphStyle(name='final_titles', fontName='Helvetica-Bold', fontSize=12, leading=12))
        styles.add(ParagraphStyle(name='table_titles', fontName='Helvetica-Bold', fontSize=8, leading=8))
        styles.add(ParagraphStyle(name='table_content', fontName='Helvetica', fontSize=8, leading=8))

        width, height = letter
    
        Story = []

        Story.append(Image(GlobalSettings.objects.first().logo_notice, height=50, width=125, hAlign='CENTER'))

        text = "Aviso de Actividad de " + self.category.name
        Story.append(Paragraph(text, styles["main_title"]))
        Story.append(Spacer(1, 12))

        if self.cau_contact:
            ## Table: Contacto CAU
            table_data = []
            table_data.append([Paragraph("Contacto CAU: ", styles["notice_bold"]), Paragraph(str(self.cau_contact), styles["notice"])])
            table_data.append([Paragraph("Teléfono contacto: ", styles["notice_bold"]), Paragraph(str(self.cau_contact.phone_number), styles["notice"])])
            table_data.append([Paragraph("Email contacto: ", styles["notice_bold"]), Paragraph(self.cau_contact.user.email, styles["notice"])])
            # Max End Date in Local Timezone
            table_data.append([Paragraph("Fecha de regreso: ", styles["notice_bold"]), Paragraph(tz.localtime(self.max_end_date).strftime('%d-%b-%Y'), styles["notice"])])
            table_data.append([Paragraph("Hora de regreso: ", styles["notice_bold"]), Paragraph(tz.localtime(self.max_end_date).strftime('%H:%M'), styles["notice"])])


            table_max_width = 1.4*inch
            table_max_width = max(table_max_width, stringWidth(str(self.cau_contact), styles["notice"].fontName, styles["notice"].fontSize)/2 + 0.2*inch)
            table_max_width = max(table_max_width, stringWidth(str(self.cau_contact.phone_number), styles["notice"].fontName, styles["notice"].fontSize) + 0.2*inch)
            table_max_width = max(table_max_width, stringWidth(self.cau_contact.user.email, styles["notice"].fontName, styles["notice"].fontSize) + 0.18*inch)
            table_max_width = max(table_max_width, stringWidth(tz.localtime(self.max_end_date).strftime('%d-%b-%Y'), styles["notice"].fontName, styles["notice"].fontSize) + 0.2*inch)
            table_max_width = max(table_max_width, stringWidth(tz.localtime(self.max_end_date).strftime('%H:%M'), styles["notice"].fontName, styles["notice"].fontSize) + 0.2*inch)

            # idea: hacer height dinámico, dependiente del contenido de la fila
            table = Table(table_data, colWidths=[1.5*inch, table_max_width], rowHeights=[0.16*inch, 0.16*inch, 0.16*inch, 0.16*inch, 0.16*inch], hAlign='RIGHT')
            table.setStyle(TableStyle([]))
            Story.append(table)
        
        # Draw Horizontal Line
        Story.append(HRFlowable(width=width, thickness=1, lineCap='square', color='#000000'))
        Story.append(Spacer(1, 12))

        ## Table: Resumen Salida
        table_data = []
        table_data.append([Paragraph('Actividad:', styles['notice_bold']), Paragraph(self.category.name, styles['notice'])])
        table_data.append([Paragraph('Nombre cerro o sector:', styles['notice_bold']), Paragraph(self.location, styles['notice'])])
        table_data.append([Paragraph('Ruta:', styles['notice_bold']), Paragraph(self.route, styles['notice'])])

        table = Table(table_data, colWidths=[2*inch, 6*inch], rowHeights=[0.2*inch, 0.2*inch, 0.2*inch], hAlign='LEFT')
        table.setStyle(TableStyle([]))
        Story.append(table)
        Story.append(Spacer(1, 12))

        ## Table: Participantes
        text = "Participantes"
        Story.append(Paragraph(text, styles["subtitles"]))
        Story.append(Spacer(1, 8))

        table_data = []
        table_data.append([
            Paragraph('', styles['table_titles']),
            Paragraph("Nombre", styles['table_titles']),
            Paragraph("Rut", styles['table_titles']),
            Paragraph("Teléfono", styles['table_titles']),
            Paragraph("Contacto Emergencia", styles['table_titles']),
            Paragraph("Teléfono Contacto Emergencia", styles['table_titles'])
            ])
        counter = 0
        for participant in self.participants.all():
            counter += 1
            if participant.main_emergencycontact:
                print(participant)
                print(participant.rut)
                print(participant.phone_number)            
                table_data.append([
                    Paragraph(str(counter), styles['table_titles']),
                    Paragraph(str(participant), styles['table_content']),
                    Paragraph(str(participant.rut), styles['table_content']),
                    Paragraph(str(participant.phone_number), styles['table_content']),
                    Paragraph(str(participant.main_emergencycontact), styles['table_content']),
                    Paragraph(str(participant.main_emergencycontact.phone_number), styles['table_content'])
                    ])
            else:
                print(participant)
                print(participant.rut)
                print(participant.phone_number)
                table_data.append([
                    Paragraph(str(counter), styles['table_titles']),
                    Paragraph(str(participant), styles['table_content']),
                    Paragraph(str(participant.rut), styles['table_content']),
                    Paragraph(str(participant.phone_number), styles['table_content']),
                    Paragraph("NO TIENE CONTACTO DE EMERGENCIA", styles['table_content']),
                    Paragraph("", styles['table_content'])
                    ])
        
        for friend in self.friends.all():
            counter += 1
            table_data.append([
                Paragraph(str(counter), styles['table_titles']),
                Paragraph(str(friend), styles['table_content']),
                Paragraph(str(friend.rut), styles['table_content']),
                Paragraph(str(friend.phone_number), styles['table_content']),
                Paragraph(str(friend.emergencycontact_name), styles['table_content']),
                Paragraph(str(friend.emergencycontact_phone), styles['table_content'])
                ])

        table = Table(table_data, colWidths=[0.2*inch, 2*inch, 1*inch, 1.25*inch, 2*inch, 1.25*inch], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
        Story.append(table)
        Story.append(Spacer(1, 12))

        ## Table: itinerario breve
        text = "Itinerario Acordado Principal"
        Story.append(Paragraph(text, styles["subtitles"]))
        Story.append(Spacer(1, 8))

        table_data = []
        table_data.append([Paragraph("Fecha de salida: ", styles["notice_bold"]), Paragraph(tz.localtime(self.start_date).strftime('%d-%b-%Y, %H:%M'), styles["notice"])])
        table_data.append([Paragraph("Fecha de llegada máxima: ", styles["notice_bold"]), Paragraph(tz.localtime(self.max_end_date).strftime('%d-%b-%Y, %H:%M'), styles["notice"])])

        table = Table(table_data, colWidths=[2*inch, 2*inch], hAlign='LEFT')
        table.setStyle(TableStyle([]))
        Story.append(table)
        Story.append(Spacer(1, 12))

        ## Table: Transporte
        text = "Transporte"
        Story.append(Paragraph(text, styles["subtitles"]))
        Story.append(Spacer(1, 8))

        table_data = []
        table_data.append([
            Paragraph("Dueño", styles['table_titles']),
            Paragraph("Marca", styles['table_titles']),
            Paragraph("Modelo", styles['table_titles']),
            Paragraph("Color", styles['table_titles']),
            Paragraph("Patente", styles['table_titles']),
            Paragraph("Lugar de Estacionamiento", styles['table_titles']),
            ])
        counter = 0
        for car in self.cars.all():
            counter += 1
            table_data.append([
                Paragraph(str(car.member), styles['table_content']),
                Paragraph(car.brand, styles['table_content']),
                Paragraph(car.model, styles['table_content']),
                Paragraph(car.color, styles['table_content']),
                Paragraph(car.license_plate, styles['table_content']),
                Paragraph(self.parking_location, styles['table_content'])
                ])

        table = Table(table_data, colWidths=[2*inch, inch, inch, inch, inch, 1.7*inch], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
        Story.append(table)
        if self.other_transportation:
          Story.append(Spacer(1, 8))
          Story.append(Paragraph("Otros medios de transporte: " + self.other_transportation, styles['table_content']))
        Story.append(Spacer(1, 12))


        ## Table: Datos Médicos Importantes
        text = "Datos Médicos Importantes"
        Story.append(Paragraph(text, styles["subtitles"]))
        Story.append(Spacer(1, 8))

        table_data = []
        table_data.append([
            Paragraph("Nombre", styles['table_titles']),
            Paragraph("Enfermedades", styles['table_titles']),
            Paragraph("Medicamentos", styles['table_titles']),
            Paragraph("Comentarios", styles['table_titles']),
            ])
        counter = 0
        for participant in self.participants.all():
            counter += 1
            table_data.append([
                Paragraph(str(participant), styles['table_content']),
                Paragraph(str(participant.medicalrecord.sicknesses), styles['table_content']),
                Paragraph(str(participant.medicalrecord.medications), styles['table_content']),
                Paragraph(str(participant.medicalrecord.comments), styles['table_content']),
                ])
        for friend in self.friends.all():
            counter += 1
            table_data.append([
                Paragraph(str(friend), styles['table_content']),
                Paragraph(str(friend.sicknesses), styles['table_content']),
                Paragraph(str(friend.medications), styles['table_content']),
                Paragraph(str(friend.comments), styles['table_content']),
                ])

        table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch, 1.7*inch], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
        Story.append(table)
        Story.append(Spacer(1, 12))

        ## Table: Observaciones
        text = "Observaciones"
        Story.append(Paragraph(text, styles["subtitles"]))
        Story.append(Spacer(1, 8))

        table_data = []
        table_data.append([
            Paragraph(self.description, styles['table_content']),
            ])
        table = Table(table_data, colWidths=[7.7*inch], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
        Story.append(table)
        Story.append(Spacer(1, 12))

        Story.append(PageBreak())

        ## Info Final
        text = "Cuerpos de Rescate Oficiales"
        Story.append(Paragraph(text, styles["final_titles"]))
        Story.append(Spacer(1, 8))
        text = "Contacto Cuerpo Socorro Andino (CSA): 136"
        Story.append(Paragraph(text, styles["notice_bold"]))
        text = "Carabineros: 133"
        Story.append(Paragraph(text, styles["notice_bold"]))
        Story.append(Spacer(1, 8))

        text = "Responsabilidad de la Cordada"
        Story.append(Paragraph(text, styles["final_titles"]))
        Story.append(Spacer(1, 8))

        Story.append(ListFlowable([
            ListItem(Paragraph("Hacer su aviso de salida de forma completa y responsable y enviarlo al egroup Montañismo UC.", styles["final_content"])),
            ListItem(Paragraph("Buscar alguien responsable y que se encuentre disponible y dispuesto a ejercer la función de Contacto CAU para su salida.", styles["final_content"])),
            ListItem(Paragraph("Informar a su contacto CAU sobre los detalles de la salida, su motivación y sus ambiciones.", styles["final_content"])),
            ListItem(Paragraph("Tomar decisiones en terreno que respeten la hora de retorno señalada para evitar la activación de los protocolos de emergencia y el gasto de recursos económicos y humanos de forma innecesaria.", styles["final_content"])),
            ListItem(Paragraph("Dar aviso de su retorno antes de la hora señalada en el aviso de salida.", styles["final_content"])),
            ListItem(Paragraph("En caso de accidente dar primeros auxilios al accidentado y luego comunicarse directamente con el contacto CAU quién activará el protocolo de emergencia.", styles["final_content"])),
            ], bulletType='bullet', start='-', bulletFontName='Helvetica', bulletFontSize=8))
            

        Story.append(Spacer(1, 8))
        text = "Responsabilidad del Contacto CAU"
        Story.append(Paragraph(text, styles["final_titles"]))
        Story.append(Spacer(1, 8))

        Story.append(ListFlowable([
            ListItem(Paragraph("Informarse de los detalles de la salida de la cordada a monitorear.", styles["final_content"])),
            ListItem(Paragraph("Tener conocimiento del protocolo de emergencia a activar en caso de emergencia.", styles["final_content"])),
            ListItem(Paragraph("Estar disponible y “contactable” para verificar el retorno o no retorno de la cordada.", styles["final_content"])),
            ListItem(Paragraph("Dar aviso del retorno o no retorno de la cordada según corresponda.", styles["final_content"])),
            ListItem(Paragraph("En caso de no retorno o accidente confirmado activar el protocolo de emergencia.", styles["final_content"])),
            ], bulletType='bullet', start='-', bulletFontName='Helvetica', bulletFontSize=8))

        Story.append(Spacer(1, 8))
        text = "Protocolo de Emergencia para Contacto CAU:"
        Story.append(Paragraph(text, styles["final_titles"]))
        Story.append(Spacer(1, 8))

        Story.append(ListFlowable([
            ListItem(Paragraph("Caso de No Retorno:", styles["final_content_bold"]), leftIndent=30),
            ], bulletType='bullet', start='1)', bulletFontName='Helvetica-Bold', bulletFontSize=8, leftIndent=10))
        Story.append(Spacer(1, 8))

        Story.append(ListFlowable([
            ListItem(Paragraph("Intentar comunicación o seguimiento de la cordada a través del dispositivo InReach y de la página MapShare.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("En caso de no tener información, dar aviso a los cuerpos oficiales de rescate (CSA y GOPE) del no retorno de la cordada entregando toda la información recopilada en el aviso de salida.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Preguntar a los cuerpos de rescate qué tipo de información, recursos humanos, técnicos o de equipo podría aportar el CAU en el procedimiento.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Avisar a los contactos de emergencia de la situación, explicándoles que lo más posible es que se trate de un retraso y no de un accidente. Informar que ya se le dio aviso a los cuerpos de rescate y que el CAU esta organizándose un grupo de apoyo para lo que sea requerido por los cuerpos de rescate.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Dar aviso por email al e-group Montañismo UC de la situación y solicitar apoyo de lo señalado por los cuerpos de rescate. El DT se encargará de convocar en primera instancia un grupo de búsqueda que pueda prepararse y permanecer “en espera” en caso de ser requerido.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Mantener al club informado a través del e-group de los acontecimientos importantes.", styles["final_content"]), leftIndent=50),
            ], bulletType='bullet', start='-', bulletFontName='Helvetica', bulletFontSize=8, leftIndent=10))
        Story.append(Spacer(1, 8))

        Story.append(ListFlowable([
            ListItem(Paragraph("Caso de Accidente Confirmado:", styles["final_content_bold"]), leftIndent=30),
            ], bulletType='bullet', start='2)', bulletFontName='Helvetica-Bold', bulletFontSize=8, leftIndent=10))
        Story.append(Spacer(1, 8))

        Story.append(ListFlowable([
            ListItem(Paragraph("Mantener la calma y obtener información de cómo sucedió el accidente, número de accidentados, lesiones diagnosticadas, ubicación geográfica, la atención de primeros auxilios entregada y de la gravedad de la situación.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Pedir al que da aviso de accidente que en lo posible permanezca disponible como primera fuente en caso de requerir más información por los cuerpos de rescate.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Dar aviso a los cuerpos oficiales de rescate (CSA y GOPE) del accidente de la cordada entregando toda la información entregada por la cordada y la recopilada en el aviso de salida.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Preguntar a los cuerpos de rescate qué tipo de información, recursos humanos, técnicos o de equipo podría aportar el CAU en el procedimiento.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Avisar a los contactos de emergencia de la situación. Informar que ya se le dio aviso a los cuerpos de rescate y que el CAU esta organizándose un grupo de apoyo para lo que sea requerido por los cuerpos de rescate. Mantengan la calma.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Dar aviso por email al e-group Montañismo UC de la situación y solicitar apoyo de lo señalado por los cuerpos de rescate. El DT se encargará de convocar en primera instancia un grupo de rescate que pueda prepararse y permanecer “en espera” en caso de ser requerido.", styles["final_content"]), leftIndent=50),
            ListItem(Paragraph("Mantener al club informado a través del e-group de los acontecimientos importantes.", styles["final_content"]), leftIndent=50),
            ], bulletType='bullet', start='-', bulletFontName='Helvetica', bulletFontSize=8, leftIndent=10))
        Story.append(Spacer(1, 8))

        doc.build(Story)

        return doc

    def mail(self, publication=False, arrival=False, late=False, cancel=False, mail_content=None):
        beta_version = True
        mail_title = 'Aviso de Salida Corta: ' + self.location
        notice_summary = 'Lugar: ' + str(self.location)
        notice_summary += '\n\nRuta: ' + str(self.route)
        notice_summary += '\n\nFecha de Salida: ' + str(tz.localtime(self.start_date).strftime('%d-%b-%Y, %H:%M'))
        notice_summary += '\n\nFecha de Llegada: ' + tz.localtime(self.max_end_date).strftime('%d-%b-%Y, %H:%M')
        notice_summary += '\n\nParticipantes: ' + str(self.participants_tostring())
        notice_summary += '\n\nContacto CAU: ' + str(self.cau_contact)
        notice_summary += '\n\nLink al aviso de salida: https://socios.cau.cl/avisos/' + str(self.id)

        if publication:
            if mail_content:
                mail_content = mail_content
            else:
                mail_content = 'Sin contenido.'
            mail_sender = settings.DEFAULT_FROM_EMAIL
            mail_recipients = self.email_recipients.all()
        elif late:
            if GlobalSettings.objects.first().notice_late_mail_content:
              mail_content = GlobalSettings.objects.first().notice_late_mail_content
            else:
              mail_content = 'Notificación de salida atrasada respecto a su fecha de llegada máxima. Si la información es errónea, por favor actualizar llegada en el sitio web de socios CAU.'
            mail_sender = settings.DEFAULT_FROM_EMAIL
            mail_recipients = self.email_late_alert_recipients.all()
        elif arrival:
            if GlobalSettings.objects.first().notice_arrival_mail_content:
              mail_content = GlobalSettings.objects.first().notice_arrival_mail_content
            else:
              mail_content = 'Notificación de llegada de la cordada.'
            if self.arrival_message:
                mail_content += '\n\n' + self.arrival_message
            mail_sender = settings.DEFAULT_FROM_EMAIL
            mail_recipients = self.email_recipients.all() # ESTÁ BIEN PORQUE DEBE SER LA MISMA GENTE QUE RECIBIÓ EL AVISO INICIALMENTE
        elif cancel:
            mail_content = 'Salida Cancelada' # Debiera incluirse un texto de llegada? como funcionaría esto?
            mail_sender = settings.DEFAULT_FROM_EMAIL
            mail_recipients = self.email_recipients.all() # ESTÁ BIEN PORQUE DEBE SER LA MISMA GENTE QUE RECIBIÓ EL AVISO INICIALMENTE
        else:
            return

        mail_content += '\n\n' + notice_summary
        
        if beta_version:
            mail_content += '\n\n' + 'Esta es una versión beta del sistema de avisos. Si tiene problemas con el sistema, por favor contacte a los administradores.'
        
        #######################################
        # Versión nueva con HTML embellecido
        #######################################
        html_content = render_to_string("emails/shortnotice.html", {
            "notice": self,
            "mail_content": mail_content,
        })

        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=mail_title,
            body=text_content,
            from_email=mail_sender,
            to=list(mail_recipients.values_list("email", flat=True)),
            reply_to=[self.sent_by.user.email] if self.sent_by else None,
        )

        email.attach_alternative(html_content, "text/html")

        # Attach PDF if needed
        if publication and self.include_pdf:
            buff = io.BytesIO()
            pdf_name = "Aviso de Salida - " + self.location + ".pdf"
            pdf_name = pdf_name.replace(',', ' - ')
            self.createPDF(buff, pdf_name)
            email.attach(pdf_name, buff.getvalue(), "application/pdf")

        #######################################
        # Versión anterior con texto plano
        #######################################
        # if publication and self.include_pdf:
        #     buff = io.BytesIO()
        #     pdf_name = "Aviso de Salida - " + self.location + ".pdf"
        #     pdf_name = pdf_name.replace(',', ' - ')
        #     doc = self.createPDF(buff, pdf_name)
        #     email = EmailMessage(subject=mail_title, body=mail_content, from_email=mail_sender, to=mail_recipients, attachments=[(pdf_name, buff.getvalue(), 'application/pdf')])
        # else:
        #     email = EmailMessage(subject=mail_title, body=mail_content, from_email=mail_sender, to=mail_recipients)        

        email.send()
    
    @property
    def time_left_for_arrival(self):
        now = tz.now()
        result = self.max_end_date - now
        return result.total_seconds()

    class Meta:
        ordering = ['status', '-max_end_date']

class ShortNotice(BaseNotice):
    class Meta:
        verbose_name = 'Aviso Rápido'
        verbose_name_plural = 'Avisos Rápidos'
        ordering = ['-start_date']

    def __str__(self):
        return str(self.start_date.date()) + " - " + self.category.name + ": " + self.location + " - " + self.route

    # definir como asociar members con emergency contacts
  
  # OJO que esto no está funcionando con basenotice así que recordarlo cuando sea implementado
@receiver(post_save, sender=ShortNotice)
def notice_handler(sender, instance, created, **kwargs):
    if created:
        if instance.status == instance.DRAFT:
            if instance.max_end_date <= tz.now():
                # LÓGICA PENDIENTE
                print("Aviso está atrasado y no debiera ser publicado")
                instance.cancel_notice()
            elif instance.start_date <= tz.now():
                # PODRÍA ALERTARSE QUE NO SE HA PUBLICADO AÚN
                print("Hora de salida ya pasó y debiera publicarse ASAP")
