
from ast import Continue
import re
from rest_framework.decorators import *;
from rest_framework.response import *;
from django.http import HttpResponse, JsonResponse
from polls.models import Person,res_done,reservations,cancel_request,Person_reduce_shift,archive_res_done
from rest_framework.views import *
import json
import datetime as dt
from django.utils import timezone
import calendar

if timezone.now().today().day==17:
  l=list(res_done.objects.all())
  for i in range(0,len(l)):
   a=archive_res_done(reservations_id=l[i].reservations_id,person_id=l[i].person_id,month_number= timezone.now().today().month)
   a.save()
  res_done.objects.all().delete()  
#get function for get allinfo for all ambulance
def getinfo_All(request):
    p=list(Person.objects.values())
    return JsonResponse(p,safe=False)
def getALL_reservsrtionCancel(request):
    p=list(cancel_request.objects.values())
    return JsonResponse(p,safe=False)    
#get function for get all reservation can book it by ambulance
def getreservation_All(request):
    c=list(reservations.objects.values())
    return JsonResponse(c,safe=False)
#post function test if the login is done succesfully
@api_view(['POST'])
def login(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    username=body['username']
    password=body['password']
    try:
        p=Person.objects.get(username=username,password=password)    
        if p.rank=="admin":
         jsonObject=toJSON(p)
         del jsonObject['_state']#to delete coulumn named is state
         jsonObject['result']='admin'
         return JsonResponse(jsonObject)
        else :
         jsonObject=toJSON(p)
         del jsonObject['_state']#to delete coulumn named is state
         jsonObject['result']='volunteer'
         return JsonResponse(jsonObject) 
    except:
        return JsonResponse({'result':'invalid'})
#function convert to json
def toJSON(p):
    return json.loads(json.dumps(p, default=lambda o: o.__dict__))   
@api_view(['POST']) 
def count_shift_post(request):
   body_unicode = request.body.decode('utf-8')
   body = json.loads(body_unicode)
   pid=body['pid']
   count1=res_done.objects.filter(person_id=pid).count()
   result={'count_of_shift':count1}
   return JsonResponse(result)
#post function for booking the reservation
def count_shift(i):
 count1=res_done.objects.filter(person_id=i).count()
 return count1
def count_of_female_in_shift(rid):
 count=0
 r= res_done.objects.filter(reservations_id=rid)
 for i in r:
  p=i.person_id
  k=Person.objects.get(id=p)
  if k.gender=='female':
       count=count+1
 return count        
#post function return reservations by person id
@api_view(['POST']) 
def myreservations(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    pid =body['pid']
    r=list(res_done.objects.filter(person_id=pid))
    a=[]
    for x in r:
     print(x)   
     k=x.reservations_id
     e=reservations.objects.get(id=k)
     a.append(e)
    jsonObject=toJSON(a) 
    return JsonResponse(jsonObject,safe=False)            
@api_view(['POST']) 
def reservepost_cancel(request):
 #if isNowInTimePeriod(dt.time(16,00), dt.time(19,30), timezone.now().time()):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  rid =body['rid']
  pid1=body['pid1']
  fullName=body['fullName']
  l=reservations.objects.get(id=rid)
  k=int(l.day_in_month)
  r=res_done.objects.filter(reservations_id=rid,person_id=pid1)
  if timezone.now().today().day==k-1:
   if r:
    try :
     g=Person.objects.get(fullName=fullName)
     pid2=g.id
     q=cancel_request.objects.filter(reservations_id=rid,person_wantcancel_id=pid1,person_substitute_id=pid2,response_to_request='pending')
     if q:
      return JsonResponse({'result':'طلب الالغاء تم ارساله مسبقا'})  
     else: 
      req=cancel_request(reservations_id=rid,person_wantcancel_id=pid1,person_substitute_id=pid2,response_to_request='pending')
      print(cancel_request(reservations_id=rid,person_wantcancel_id=pid1,person_substitute_id=pid2,response_to_request='pending'))
      req.save() 
      return JsonResponse({'result':'تم ارسال طلب الالغاء بنجاح'})
    except:
       return JsonResponse({'result':'يجب ادخال اسم صحيح'})  
   else :
     return JsonResponse({'result':'هذه المناوبة غير محجوزة باسمك'}) 
  else:
    return JsonResponse({'result':'لا يمكنك الا ان تلغي مناوبات الغد'})    
 #else:
    return JsonResponse({'result':'لا يمكنك الا ان تلغي مناوبات في هذا الوقت'})   
     
@api_view(['POST']) 
def query_about_cancel(request):
 #if isNowInTimePeriod(dt.time(20,00), dt.time(23,30), timezone.now().time()):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  pid1 =body['pid1']
  result=[] 
  q=cancel_request.objects.filter(person_wantcancel_id=pid1)
  if len(q)>0: 
     for j in q:
      if j.response_to_request=='accept':
        
         s=j.reservations_id
         v=reservations.objects.get(id=s)
         k=int(v.day_in_month)
         if timezone.now().today().day==k:          
          pid2=j.person_substitute_id
          s=j.reservations_id
          jsonObject={}
          v=reservations.objects.get(id=s)
          jsonObject['result']='تم الغاء المناوبة عند التاريخ '+v.day_in_month+" "+v.shift_time
          cancel_request.objects.filter(person_wantcancel_id=pid1,reservations_id=s,response_to_request='not accept').delete()
          result.append(jsonObject)   
          res_done.objects.filter(reservations_id=s,person_id=pid1).update(person_id=pid2)
     for jj in q: 
        if jj.response_to_request=='not accept':
         if len(cancel_request.objects.filter(person_wantcancel_id=pid1,reservations_id=s,response_to_request='accept'))>0:
           continue
         s=jj.reservations_id
         v=reservations.objects.get(id=s)
         k=int(v.day_in_month)
         if timezone.now().today().day==k:          
          s=jj.reservations_id
          jsonObject={}
          v=reservations.objects.get(id=s)
          jsonObject['result']='لم يتم الغاء المناوبة عند التاريخ '+v.day_in_month+" "+v.shift_time
          
          result.append(jsonObject) 
        elif jj.response_to_request!='not accept' and jj.response_to_request!='accept': 
          break
     seen = set()
     new_l = []
     for d in result:
       t = tuple(d.items())
       if t not in seen:
         seen.add(t)
         new_l.append(d)
     print(new_l)
     if len(new_l)==0:
        jsonObject={}
        jsonObject['result']="لم يتم الرد من قبل الادمن"
        new_l.append( jsonObject)
     if len(new_l)==1:
       jsonObject={}
       jsonObject['result']=""
       new_l.append( jsonObject)
     return JsonResponse(new_l,safe=False)  

  else:
   a=[{"result":'لم تقوم بطلب الغاء'},{"result":""}]
   return JsonResponse(a,safe=False)
#  #else:
#      a=[{"result":'لا يمكنك الاستعلام في هذا الوقت'},{"result":""}]
#    return JsonResponse(a,safe=False)
@api_view(['POST']) 
def cancel_requests_for_admin(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  pid =body['pid']
  r=cancel_request.objects.all()
  cancel_req=[]
  for j in r:
    jsonObject=toJSON(j)
    del jsonObject['_state']#to delete coulumn named is state
    del jsonObject['id']
    cancel_req.append(jsonObject)
  return JsonResponse(cancel_req,safe=False) 







@api_view(['POST']) 
def accept_button(request):  

   body_unicode = request.body.decode('utf-8')
   body = json.loads(body_unicode)
   rid =body['rid']
   pid1 =body['pid1']
   pid2=body['pid2']
   res_done.objects.filter(reservations_id=rid,person_id=pid1).update(person_id=pid2)
   cancel_request.objects.filter( person_wantcancel_id=pid1,person_substitute_id=pid2,reservations_id=rid).update(response_to_request="accept")
   return JsonResponse({'result':'تم القبول'})  

@api_view(['POST']) 
def valid_reservation(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  pid =body['pid']
  weekNumber=body['weekNumber']
  c=list(reservations.objects.all())
  valid=[]
  l=len(c)
  if weekNumber=='الأسبوع الأول':
   for j in range(1,22):
    print(j) 
    i=j
    pp=Person.objects.get(id=pid)
    if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
           
    elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
    elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')    
   valid.insert(0, '1')   
   valid.insert(4, '2')  
   valid.insert(8, '3')   
   valid.insert(12, '4')     
   valid.insert(16, '5')  
   valid.insert(20, '6')  
   valid.insert(24, '7')  
  elif weekNumber=='الأسبوع الثاني':
    
   for j in range(22,43):
    print(j)
    i=j
    pp=Person.objects.get(id=pid)
    if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
    elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
    elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
   valid.insert(0, '8')   
   valid.insert(4, '9')  
   valid.insert(8, '10')   
   valid.insert(12, '11')     
   valid.insert(16, '12')  
   valid.insert(20, '13')  
   valid.insert(24, '14')             
  elif weekNumber=='الأسبوع الثالث':
    
   for j in range(43,64):
    print(j)
    i=j
    pp=Person.objects.get(id=pid)
    if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
    elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
    elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')     
   valid.insert(0, '15')   
   valid.insert(4, '16')  
   valid.insert(8, '17')   
   valid.insert(12, '18')     
   valid.insert(16, '19')  
   valid.insert(20, '20')  
   valid.insert(24, '21')         
  elif weekNumber=='الأسبوع الرابع':
    
   for j in range(64,85):
    print(j)
    i=j
    pp=Person.objects.get(id=pid)
    if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
    elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
    elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')       
   valid.insert(0, '22')   
   valid.insert(4, '23')  
   valid.insert(8, '24')   
   valid.insert(12, '25')     
   valid.insert(16, '26')  
   valid.insert(20, '27')  
   valid.insert(24, '28')           
  elif weekNumber== 'الأسبوع الخامس':
   now= timezone.now()
   if calendar.monthrange(now.year, now.month)[1]==31:
    for j in range(85,94):
     print(j)
     i=j
     pp=Person.objects.get(id=pid)
     if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
     elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
     elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')  
    for i in range (0,16):
           valid.append('') 
    valid.insert(0, '29')   
    valid.insert(4, '30')  
    valid.insert(8, '31')                     
   if calendar.monthrange(now.year, now.month)[1]==30:
    for j in range(85,91):
     print(j)
     i=j
     pp=Person.objects.get(id=pid)
     if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
     elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
     elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')      
    for i in range (0,20):
           valid.append('')   
    valid.insert(0, '29')   
    valid.insert(4, '30')  
                 
   if calendar.monthrange(now.year, now.month)[1]==29:
    for j in range(85,88):
     print(j)
     i=j
     pp=Person.objects.get(id=pid)
     if pp.rank=='scout':   
      rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9  or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      elif p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif  res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')   
     elif pp.rank=='leader':
    
      rr=res_done.objects.filter(reservations_id=i,person_rank="leader")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  : 
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')
     elif pp.rank=='sought':
      rr=res_done.objects.filter(reservations_id=i,person_rank="sought")    
      p= Person.objects.get(id=pid) 
      if p.gender=='male':
       if res_done.objects.filter(reservations_id=i,person_id=pid):
         valid.append('حجزته مسبقا') 
       elif res_done.objects.filter(reservations_id=i).count()>=9 or rr.count()>=3  :  
        valid.append('غير متاح')
       else:
        valid.append('متاح')
      if p.gender=='female': 
        if res_done.objects.filter(reservations_id=i,person_id=pid):
          valid.append('حجزته مسبقا') 
        elif res_done.objects.filter(reservations_id=i).count()>=9 or count_of_female_in_shift(i)>=5 or  is_third(i) or rr.count()>=3:
          valid.append('غير متاح')
        else :
          valid.append('متاح')        
    for i in range (0,24):
           valid.append('') 
    valid.insert(0, '29')   
              
   if calendar.monthrange(now.year, now.month)[1]==28:
     for j in range(0,28):
          valid.append('')     
  return JsonResponse(valid,safe=False)
@api_view(['POST'])
def reservepost(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  print(body)
  rid =body['rid']
  pid =body['pid']
  u=Person_reduce_shift.objects.filter(person_id=pid)
  if u.exists() and len(rid)<int(u[0].number_of_shift):
     l=reservations(day_in_month="",shift_time="")
     jsonObject=toJSON(l)
     del jsonObject['_state']
     del jsonObject['id']
     jsonObject['message']='يجب تحديد مناوبات حسب طلب التخفيض'
     return JsonResponse(jsonObject)
  if u.exists()==False and len(rid)<12:
    l=reservations(day_in_month="",shift_time="")
    jsonObject=toJSON(l)
    del jsonObject['_state']
    del jsonObject['id']
    jsonObject['message']='يجب تحديد 12 مناوبة على الاقل'
    return JsonResponse(jsonObject)
  if len(rid) != len(set(rid))  :
    l=reservations(day_in_month="",shift_time="")
    jsonObject=toJSON(l)
    del jsonObject['_state']
    del jsonObject['id']
    jsonObject['message']='ثمت بتحديد مناوبة اكثر من مرة'
    return JsonResponse(jsonObject)
  else:  
   result=[]  
   pp=Person.objects.get(id=pid)
   if pp.rank=='scout':
    # if (timezone.now().today().day==11 and  isNowInTimePeriod(dt.time(16,00), dt.time(21,30), timezone.now().time()))or(timezone.now().today().day==10 and  isNowInTimePeriod(dt.time(12,00), dt.time(1,59), timezone.now().time())) :
     if count_shift(pid)!=0:
       l=reservations(day_in_month="",shift_time="")
       jsonObject=toJSON(l)
       del jsonObject['_state']
       del jsonObject['id']
       jsonObject['message']='قمت بالحجز مسبقا'
       return JsonResponse(jsonObject)
     for i in rid:
       
       r=res_done.objects.filter(reservations_id=i) 
       if r.count()>=9:
        l=reservations.objects.get(id=i)
        jsonObject=toJSON(l)
        del jsonObject['_state']
        del jsonObject['id']
        jsonObject['message']=' الفريق مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
        result.append(jsonObject)   
       rr=res_done.objects.filter(reservations_id=i,person_rank="scout")
       if rr.count()>=3:
             l=reservations.objects.get(id=i)
             print(l.shift_time)
             jsonObject=toJSON(l)
             del jsonObject['_state']
             del jsonObject['id']
             jsonObject['message']='فريق الكشاف مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
             result.append(jsonObject)
       else:
                try:
                   p=Person.objects.get(id=pid,gender="male")
                   count=0
                   for i in rid:
                    if is_third(i)==True:
                     count=count+1
                   print(count)  
                   if count<3:
                     l=reservations.objects.get(id=i)
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['day_in_month']=""
                     jsonObject['shift_time']=""
                     jsonObject['message']='يجب عليك حجز 3 مناوبات فترة ثالثة'
                     result.append(jsonObject)
                     break 
                   if test_if_3_shift_series(rid):
                     l=reservations.objects.get(id=i)
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['day_in_month']=""
                     jsonObject['shift_time']=""
                     jsonObject['message']='لا يمكنك حجز ثلاث مناوبات متتالية'
                     result.append(jsonObject)
                     break 
                except: 
                   p=Person.objects.get(id=pid,gender="female")
                   if count_of_female_in_shift(i)>=5:
                    l=reservations.objects.get(id=i) 
                    jsonObject=toJSON(l)
                    del jsonObject['_state']
                    del jsonObject['id']
                    jsonObject['message']='عدد المسعفات مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
                    result.append(jsonObject)
                   elif is_third(i):
                     l=reservations.objects.get(id=i) 
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['message']='لا يمكنك حجز مناوبة فترة ثالثة'
                     result.append(jsonObject)  
     if result==[]:
       l=reservations(day_in_month="",shift_time="")
       jsonObject=toJSON(l)
       del jsonObject['_state']
       del jsonObject['id']
       jsonObject['message']='تم الحجز بنجاح'
       for i in rid:
        k=Person.objects.get(id=pid)
        m=k.rank
        rr=res_done(reservations_id=i,person_id=pid,person_rank=m)
        rr.save()
       return JsonResponse(jsonObject)
     else:   
      print("hiii") 
      return JsonResponse(result,safe=False)     
    # else:
    #    l=reservations(day_in_month="",shift_time="")
    #    jsonObject=toJSON(l)
    #    del jsonObject['_state']
    #    del jsonObject['id']
    #    jsonObject['day_in_month']=""
    #    jsonObject['shift_time']=""
    #    jsonObject['message']='لا يمكنك الحجز في هذا الوقت' 
    #    return JsonResponse(jsonObject)
   if pp.rank=='leader':    
    # if (timezone.now().today().day==10 and  isNowInTimePeriod(dt.time(16,00), dt.time(19,30), timezone.now().time()))or(timezone.now().today().day==10 and  isNowInTimePeriod(dt.time(12,00), dt.time(1,59), timezone.now().time())) :
     if count_shift(pid)!=0:
       l=reservations(day_in_month="",shift_time="")
       jsonObject=toJSON(l)
       del jsonObject['_state']
       del jsonObject['id']
       jsonObject['message']='قمت بالحجز مسبقا'
       return JsonResponse(jsonObject)
     for i in rid:
       print(result)
       r=res_done.objects.filter(reservations_id=i) 
       if r.count()>=9:
        l=reservations.objects.get(id=i)
        jsonObject=toJSON(l)
        del jsonObject['_state']
        del jsonObject['id']
        jsonObject['message']=' الفريق مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
        result.append(jsonObject)   
       rr=res_done.objects.filter(reservations_id=i,person_rank="leader")
       if rr.count()>=3:
             l=reservations.objects.get(id=i)
             jsonObject=toJSON(l)
             del jsonObject['_state']
             del jsonObject['id']
             jsonObject['message']='فريق القائد مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
             result.append(jsonObject)
       else:
        try:
                   p=Person.objects.get(id=pid,gender="male")
                   count=0
                   for i in rid:
                    if is_third(i)==True:
                     count=count+1
                   print(count)  
                   if count<3:
                     l=reservations.objects.get(id=i)
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['day_in_month']=""
                     jsonObject['shift_time']=""
                     jsonObject['message']='يجب عليك حجز 3 مناوبات فترة ثالثة'
                     result.append(jsonObject)
                     break 
                   if test_if_3_shift_series(rid):
                     l=reservations.objects.get(id=i)
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['day_in_month']=""
                     jsonObject['shift_time']=""
                     jsonObject['message']='لا يمكنك حجز ثلاث مناوبات متتالية'
                     result.append(jsonObject)
                     break 
        except:  
                   p=Person.objects.get(id=pid,gender="female")
                   if count_of_female_in_shift(i)>=5:
                    l=reservations.objects.get(id=i) 
                    jsonObject=toJSON(l)
                    del jsonObject['_state']
                    del jsonObject['id']
                    jsonObject['message']='عدد المسعفات مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
                    result.append(jsonObject)
                   elif is_third(i):
                     l=reservations.objects.get(id=i) 
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['message']='لا يمكنك حجز مناوبة فترة ثالثة'
                     result.append(jsonObject)  
     if result==[]:
       l=reservations(day_in_month="",shift_time="")
       jsonObject=toJSON(l)
       del jsonObject['_state']
       del jsonObject['id']
       jsonObject['message']='تم الحجز بنجاح'
       for i in rid:
        k=Person.objects.get(id=pid)
        m=k.rank
        rr=res_done(reservations_id=i,person_id=pid,person_rank=m)
        rr.save()
       return JsonResponse(jsonObject)
     else:   
      print("hiii") 
      return JsonResponse(result,safe=False)     
    # else:
    #    l=reservations(day_in_month="",shift_time="")
    #    jsonObject=toJSON(l)
    #    del jsonObject['_state']
    #    del jsonObject['id']
    #    jsonObject['day_in_month']=""
    #    jsonObject['shift_time']=""
    #    jsonObject['message']='لا يمكنك الحجز في هذا الوقت' 
      #  return JsonResponse(jsonObject)
   if pp.rank=='sought':
    # if (timezone.now().today().day==10 and  isNowInTimePeriod(dt.time(16,00), dt.time(19,30), timezone.now().time()))or(timezone.now().today().day==10 and  isNowInTimePeriod(dt.time(12,00), dt.time(1,59), timezone.now().time())) :
     if count_shift(pid)!=0:
       l=reservations(day_in_month="",shift_time="")
       jsonObject=toJSON(l)
       del jsonObject['_state']
       del jsonObject['id']
       jsonObject['message']='قمت بالحجز مسبقا'
       return JsonResponse(jsonObject)
     for i in rid:
       print(result)
       r=res_done.objects.filter(reservations_id=i) 
       if r.count()>=9:
        l=reservations.objects.get(id=i)
        jsonObject=toJSON(l)
        del jsonObject['_state']
        del jsonObject['id']
        jsonObject['message']=' الفريق مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
        result.append(jsonObject)   
       rr=res_done.objects.filter(reservations_id=i,person_rank="sought")
       if rr.count()>=3:
             l=reservations.objects.get(id=i)
             jsonObject=toJSON(l)
             del jsonObject['_state']
             del jsonObject['id']
             jsonObject['message']='فريق المسعف مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
             result.append(jsonObject)
       else:
        try:
                   p=Person.objects.get(id=pid,gender="male")
                   count=0
                   for i in rid:
                    if is_third(i)==True:
                     count=count+1
                   print(count)  
                   if count<3:
                     l=reservations.objects.get(id=i)
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['day_in_month']=""
                     jsonObject['shift_time']=""
                     jsonObject['message']='يجب عليك حجز 3 مناوبات فترة ثالثة'
                     result.append(jsonObject)
                     break 
                   if test_if_3_shift_series(rid):
                     l=reservations.objects.get(id=i)
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['day_in_month']=""
                     jsonObject['shift_time']=""
                     jsonObject['message']='لا يمكنك حجز ثلاث مناوبات متتالية'
                     result.append(jsonObject)
                     break 
        except:  
                   p=Person.objects.get(id=pid,gender="female")
                   if count_of_female_in_shift(i)>=5:
                    l=reservations.objects.get(id=i) 
                    jsonObject=toJSON(l)
                    del jsonObject['_state']
                    del jsonObject['id']
                    jsonObject['message']='عدد المسعفات مكتمل عند التاريخ'+" "+str(l.day_in_month)+ " "+str(l.shift_time)
                    result.append(jsonObject)
                   elif is_third(i):
                     l=reservations.objects.get(id=i) 
                     jsonObject=toJSON(l)
                     del jsonObject['_state']
                     del jsonObject['id']
                     jsonObject['message']='لا يمكنك حجز مناوبة فترة ثالثة'
                     result.append(jsonObject)  
     if result==[]:
       l=reservations(day_in_month="",shift_time="")
       jsonObject=toJSON(l)
       del jsonObject['_state']
       del jsonObject['id']
       jsonObject['message']='تم الحجز بنجاح'
       for i in rid:
        k=Person.objects.get(id=pid)
        m=k.rank
        rr=res_done(reservations_id=i,person_id=pid,person_rank=m)
        rr.save()
       return JsonResponse(jsonObject)
     else:   
      print("hiii") 
      return JsonResponse(result,safe=False)     
    # else:
    #    l=reservations(day_in_month="",shift_time="")
    #    jsonObject=toJSON(l)
    #    del jsonObject['_state']
    #    del jsonObject['id']
    #    jsonObject['day_in_month']=""
    #    jsonObject['shift_time']=""
    #    jsonObject['message']='لا يمكنك الحجز في هذا الوقت' 
    #    return JsonResponse(jsonObject)
                     
                  # except:
                  #   return JsonResponse({'jsonObject':'9999'})                      
          #  elif timezone.now().today().day==7 and  isNowInTimePeriod(dt.time(10,00), dt.time(11,30),timezone.now().time()):  
          #   if count_shift(pid)+len(rid)<12:
          #     return JsonResponse({'result':'you should take minimum 12 shifts in month'})   
          #   rr=res_done.objects.filter(reservations_id=i,date=date,person_rank="scout")
          #   if rr.count()>=3:
          #    return JsonResponse({'result':'you can not book it scout is full'})
          #   else:
          #     try:
          #      res_done.objects.get(reservations_id=i,date=date,person_id=pid)
          #      return JsonResponse({'result':'you already booked it'})     
          #     except:
          #       try:
          #        p=Person.objects.get(id=pid,gender="male")
          #        print('hello')
          #        print(is_third_count(pid))
          #        count=0
          #        for i in rid:
          #           if is_third(i)==True:
          #            count=count+1  
          #        if count +is_third_count(pid) <3:
          #          return JsonResponse({'result':'you should choose minimum 3 third shift'}) 
          #       except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})    
          #  elif timezone.now().today().day==7 and  isNowInTimePeriod(dt.time(9,00), dt.time(9,30),timezone.now().time()):      
          #   rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="scout")
          #   ss=res_done.objects.filter(reservations_id=rid,date=date,person_rank="sought")
          #   if rr.count()+ss.count()>=6:
          #    return JsonResponse({'result':'you can not book it scout is full'})
          #   else:
          #     try:
          #      res_done.objects.get(reservations_id=rid,date=date,person_id=pid)
          #      return JsonResponse({'result':'you already booked it'})     
          #     except:
          #       try:
          #        p=Person.objects.get(id=pid,gender="male")
          #        if count_shift(pid)==6:
          #         return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #        else:
          #          k=Person.objects.get(id=pid)
          #          if rr.count()>=3:
          #           m='sought'        
          #          else:
          #           m='scout'  
          #          mm=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #          mm.save() 
          #          return JsonResponse({'result':'Booked successfully'})   
          #       except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #             k=Person.objects.get(id=pid)
          #             if rr.count()>=3:
          #               m='sought'        
          #             else:
          #              m='scout'  
          #             mm=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #             mm.save() 
          #             return JsonResponse({'result':'Booked successfully'})    
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})
          #  else:
          #      return JsonResponse({'result':'you can not book in this time'})           
          # if pp.rank=="leader":  
          #  if timezone.now().today().day==1 and  isNowInTimePeriod(dt.time(9,30), dt.time(10,00),timezone.now().time()):  
          #   rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="leader")   
          #   if rr.count()>=3:
          #     return JsonResponse({'result':'you can not book it leader is full'})  
          #   else:
          #      try:
          #        p=Person.objects.get(id=pid,gender="male")
          #        if count_shift(pid)==0:
          #         if is_first(rid) or is_second(rid):
          #          return JsonResponse({'result':'you must book third_shift first'})
          #         else:
          #          k=Person.objects.get(id=pid)
          #          m=k.rank        
          #          rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #          rr.save()
          #          return JsonResponse({'result':'Booked successfully'})     
          #        elif count_shift(pid)==6 :
          #          return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #        else:
          #          k=Person.objects.get(id=pid)
          #          m=k.rank        
          #          rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #          rr.save()
          #          return JsonResponse({'result':'Booked successfully'})    
          #      except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})   
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})     
          #  elif timezone.now().today().day==2 and  isNowInTimePeriod(dt.time(9,30), dt.time(10,00),timezone.now().time()):  
          #   rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="leader")
          #   if rr.count()>=3:
          #    return JsonResponse({'result':'you can not book it scout is full'})
          #   else:
          #     try:
          #      res_done.objects.get(reservations_id=rid,date=date,person_id=pid)
          #      return JsonResponse({'result':'you already booked it'})     
          #     except:
          #       try:
          #        p=Person.objects.get(id=pid,gender="male")
          #        if count_shift(pid)==0:
          #         if is_first(rid) or is_second(rid):
          #          return JsonResponse({'result':'you must book third_shift first'})
          #         else:
          #          k=Person.objects.get(id=pid)
          #          m=k.rank        
          #          rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #          rr.save()
          #          return JsonResponse({'result':'Booked successfully'})    
          #        elif count_shift(pid)==6 :
          #          return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #        else:
          #          k=Person.objects.get(id=pid)
          #          m=k.rank        
          #          rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #          rr.save()
          #          return JsonResponse({'result':'Booked successfully'})
          #       except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})  
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})     
          #  elif  timezone.now().today().day==7 and  isNowInTimePeriod(dt.time(9,30), dt.time(10,00),timezone.now().time()):  
          #   rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="leader")
          #   ss=res_done.objects.filter(reservations_id=rid,date=date,person_rank="sought")   
          #   kk=res_done.objects.filter(reservations_id=rid,date=date,person_rank="scout")  
          #   if rr.count()+ss.count()+kk.count()>=9:
          #     return JsonResponse({'result':'you can not book it leader is full'})  
          #   else:
          #      try:
          #        p=Person.objects.get(id=pid,gender="male")
          #        if count_shift(pid)==6 :
          #          return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #        else:
          #          k=Person.objects.get(id=pid)
          #          if rr.count()>=3:
          #            if kk.count()>=3:
          #             m='sought'
          #            else :
          #             m='scout'
          #          else:
          #            m='leader'          
          #          mm=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #          mm.save()
          #          return JsonResponse({'result':'Booked successfully'})      
          #      except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #            k=Person.objects.get(id=pid)
          #            if rr.count()>=3:
          #             if kk.count()>=3:
          #              m='sought'
          #             else :
          #              m='scout'
          #            else:
          #             m='leader'         
          #            mm=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #            mm.save()
          #            return JsonResponse({'result':'Booked successfully'})    
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})              
          #  else:
          #      return JsonResponse({'result':'you can not book in this time'})              
          # if pp.rank=="sought":
          #  if timezone.now().today().day==1 and  isNowInTimePeriod(dt.time(10,00), dt.time(10,30),timezone.now().time()): 
          #    rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="sought")     
          #    if rr.count()>=3: 
          #       return JsonResponse({'result':'you can not book it sought is full'})
          #    else:
          #     try:
          #      res_done.objects.get(reservations_id=rid,date=date,person_id=pid)
          #      return JsonResponse({'result':'you already booked it'})     
          #     except:
          #        try:
          #         p=Person.objects.get(id=pid,gender="male")
          #         if count_shift(pid)==0:
          #          if is_first(rid) or is_second(rid):
          #           return JsonResponse({'result':'you must book third_shift first'})
          #          else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})      
          #         elif count_shift(pid)==6 :
          #          return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #         else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'}) 
                    
          #        except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})   
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})
          #  elif timezone.now().today().day==2 and  isNowInTimePeriod(dt.time(10,00), dt.time(10,30),timezone.now().time()):  
          #   rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="sought")
          #   if rr.count()>=3:
          #    return JsonResponse({'result':'you can not book it scout is full'})
          #   else:
          #     try:
          #      res_done.objects.get(reservations_id=rid,date=date,person_id=pid)
          #      return JsonResponse({'result':'you already booked it'})     
          #     except:
          #       try:
          #        p=Person.objects.get(id=pid,gender="male")
          #        if count_shift(pid)==0:
          #         if is_first(rid) or is_second(rid):
          #          return JsonResponse({'result':'you must book third_shift first'})
          #         else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})     
          #        elif count_shift(pid)==6 :
          #          return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #        else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})      
          #       except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})    
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})      
          #  elif timezone.now().today().day==7 and  isNowInTimePeriod(dt.time(10,00), dt.time(10,30),timezone.now().time()): 
          #    rr=res_done.objects.filter(reservations_id=rid,date=date,person_rank="sought")    
          #    if rr.count()>=3:
          #      return JsonResponse({'result':'you can not book it sought is full'})
          #    else:
          #     try:
          #      res_done.objects.get(reservations_id=rid,date=date,person_id=pid)
          #      return JsonResponse({'result':'you already booked it'})     
          #     except:
          #        try:
          #         p=Person.objects.get(id=pid,gender="male")
          #         if count_shift(pid)==6 :
          #          return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #         else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})         
          #        except:
          #         try:   
          #          p=Person.objects.get(id=pid,gender="female")
          #          print("123")
          #          print(count_of_female_in_shift(rid))
          #          if count_of_female_in_shift(rid)>=5:
          #           return JsonResponse({'result':'female in this shift is full'})
          #          if is_third(rid):
          #           return JsonResponse({'result':'you are female you can not book this shift'})
          #          elif count_shift(pid)==6 :
          #           return JsonResponse({'result':'you already have taken 6 shifts in this week'})
          #          else:
          #           k=Person.objects.get(id=pid)
          #           m=k.rank        
          #           rr=res_done(reservations_id=rid,date=date,person_id=pid,person_rank=m)
          #           rr.save()
          #           return JsonResponse({'result':'Booked successfully'})    
          #         except:
          #           return JsonResponse({'jsonObject':'9999'})            
          #  else:
          #    return JsonResponse({'result':'you can not book in this time'})    


def is_first(rid):
  rid=int(rid)
  l=[1,4,7,10,13,16,19,22,25,28,31,34,37,40,43,46,49,52,55,58,61,64,67,70,73,76,79,82,85,88,91]
  if rid in l:
    return True
  else:
    return False

def is_second(rid):
  rid=int(rid)
  l=[2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56,59,62,65,68,71,74,77,80,83,86,89,92]
  if rid in l:
    return True
  else:
    return False
def is_third_count(pid):
 count=0
 l=[3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72,75,78,81,84,87,90,93]
 for i in l:
  count1=res_done.objects.filter(person_id=pid,reservations_id=i).count()
  count=count+count1
  
 return count

def is_third(rid):
  rid=int(rid)
  l=[3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72,75,78,81,84,87,90,93]
  if rid in l:
    return True
  else:
    return False
from datetime import datetime, time
def isNowInTimePeriod(startTime, endTime, nowTime): 
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime  

def test_if_3_shift_series(rid)  :
  newrid=sorted(rid)
  print(newrid)
  count=0
  q=False
  for i in range(len(newrid)-1):
    if newrid[i]==newrid[i+1]-1:
      count=count+1
    else:
      count=0
    print(count) 
    if count==2:
      q=True
      break
  return q   




   