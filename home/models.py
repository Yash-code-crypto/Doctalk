from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime

# Create your models here.


from django.db.models import Q
from django.db.models.deletion import CASCADE

class PostManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(name__icontains=query))
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, default="")
    last_name = models.CharField(max_length=200, default="")
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, default="")
    address = models.CharField(max_length=200, default="")
    city = models.CharField(max_length=200, default="")
    state = models.CharField(max_length=200, default="")
    zipcode = models.CharField(max_length=200, default="")
    pic = models.ImageField(upload_to="profiles/")
    is_user = models.BooleanField()
    is_partener = models.BooleanField()



    def __str__(self):
        return self.email

class Hospital(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    pic = models.ImageField(upload_to="hospitals/")

    objects = PostManager()
 

    def __str__(self):
        return self.name

class Ambulance(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    pic = models.ImageField(upload_to="ambulance/")
    mobile = models.CharField(max_length=50)


    objects = PostManager()

    def __str__(self):
        return self.name

class MedicalStore(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    pic = models.ImageField(upload_to="medical/")
    mobile = models.CharField(max_length=50)

    objects = PostManager()

    def __str__(self):
        return self.name

class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    pic = models.ImageField(upload_to="doctor/")
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)

    objects = PostManager()

    def __str__(self):
        return self.name

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    secret_key = models.UUIDField(unique=True, default=uuid.uuid4)
    partener = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partener")
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient")
    category = models.CharField(max_length=50)
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.patient.username


class Message(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    text = models.CharField(max_length=200)
    timestamp = models.CharField(default=datetime.now(), max_length=20)

    def __str__(self):
        return self.sender.name + " > " + self.receiver.name



class Review(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,default=None,null=True)
    hospital=models.ForeignKey(Hospital,on_delete=CASCADE,default=None,null=True)
    text=models.CharField(max_length=256)

    def __str__(self):
        return self.doctor.name

        
