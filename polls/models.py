from unicodedata import name
from unittest.util import _MAX_LENGTH
from django.db import models

#all info for all ambulance 
class Person(models.Model):
    fullName=models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    password= models.CharField(max_length=200)
    username= models.CharField(max_length=200)
    gender=models.CharField(max_length=200,null=True)
    rank=models.CharField(max_length=200,null=True)
    camp=models.CharField(max_length=200,null=True)
#all reservation you can book it
class reservations(models.Model):
    day_in_month=models.CharField(max_length=200)
    shift_time=models.CharField(max_length=200)
#all info for any reservation 
class res_done(models.Model):
    reservations_id=models.CharField(max_length=200)
    person_id=models.CharField(max_length=200)
    person_rank=models.CharField(max_length=200,null=True)
class cancel_request(models.Model):
    person_wantcancel_id=models.CharField(max_length=200)
    person_substitute_id= models.CharField(max_length=200)   
    reservations_id=models.CharField(max_length=200)
    response_to_request=models.CharField(max_length=200)
class Person_reduce_shift(models.Model):
   person_id=models.CharField(max_length=200,null=True)
   fname=models.CharField(max_length=200)
   lname=models.CharField(max_length=200)
   number_of_shift=models.CharField(max_length=200)
class archive_res_done(models.Model):
    reservations_id=models.CharField(max_length=200)
    person_id=models.CharField(max_length=200)
    month_number=models.CharField(max_length=200,null=True)

    

