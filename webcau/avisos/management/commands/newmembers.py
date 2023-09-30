from django.core.management.base import BaseCommand, CommandError
import csv
from avisos.models import Member, User
import datetime

class Command(BaseCommand):
    help = "Loads new members to Users and Member models from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            counter = 0
            for row in reader:
                if counter == 0:
                    counter += 1
                    continue
                username = row[0]
                email = row[1]
                name = row[2]
                middlename = row[3]
                first_surname = row[4]
                second_surname = row[5]
                password = row[6]
                rut = row[7]
                birth_date = row[8]
                enrollment_date = row[9]
                phone = row[10]
                if Member.objects.filter(rut=rut).exists() or rut == "":
                    print("rut vacío o ya existe: " + rut)
                    continue
                if User.objects.filter(username=username).exists() or username == "":
                    print("username vacío o ya existe: " + username)
                    continue

                User.objects.create_user(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS("Successfully created user %s" % email))
                current_member = Member.objects.get(user=User.objects.get(username=username))
                current_member.rut = rut
                current_member.name = name
                current_member.middlename = middlename
                current_member.first_surname = first_surname
                current_member.second_surname = second_surname
                current_member.birth_date = datetime.datetime.strptime(birth_date, '%d-%m-%y').date() if birth_date != "" else None
                current_member.enrollment_date = datetime.datetime.strptime(enrollment_date, '%d-%m-%y').date() if enrollment_date != "" else None
                current_member.phone_number = phone
                current_member.save()
        self.stdout.write(self.style.SUCCESS("Successfully created users."))
