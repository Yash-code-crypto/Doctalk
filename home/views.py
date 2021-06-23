from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import reverse_geocoder as rg
from django.db.models import Q

from django.views.generic import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Hospital,Ambulance,MedicalStore,Doctor


from django.core.mail import send_mail

import threading


# Create your views here.

class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()

def index(request):
    username = request.user
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        is_partener = profile.is_partener
    except:
        user = None
        is_partener = None
    try:
        city = request.session['location']
    except:
        city = None
    hospitals = list(Hospital.objects.filter(city=city))
    hospitals += list(Hospital.objects.all())
    medicals = list(MedicalStore.objects.filter(city=city))
    medicals += list(MedicalStore.objects.all())
    ambulances = list(Ambulance.objects.filter(city=city))
    ambulances += list(Ambulance.objects.all())
    doctors = list(Doctor.objects.filter(city=city))
    doctors += list(Doctor.objects.all())
    doctors = set(doctors)
    context = {"location": city, 'user':user, 'is_partener':is_partener,'hospitals':set(hospitals),
    'medicals':set(medicals), 'ambulances':set(ambulances), 'doctors':set(doctors)}
    return render(request, 'index.html', context)

def signin(request):
    try:
        city = request.session['location']
    except:
        city = None
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")      
        user = authenticate(username=User.objects.get(email=email).username, password=password)  
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            context = {'error':'Invalid Email or Password.', 'location':city}
            return render(request, 'login.html', context)
    context={'location':city}
    return render(request, 'login.html')

def signup_user(request):
    try:
        city = request.session['location']
    except:
        city = None
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            if user:
                return render(request, 'register.html', {'error': 'Email Already Exist', 'location':city})
        except:
            user = None
        try:
            user = User.objects.get(username=username)
            if user:
                return render(request, 'register.html', {'error': 'Username Already Exist', 'location':city})
        except:
            user = None
        user = User.objects.create_user(email=email, username=username, password=password)
        user.save()
        profile = Profile(user=user, username=username, email=email,is_user=True, is_partener=False)
        profile.save()
        return redirect('signin')       
    return render(request, 'register.html', {'location':city})

def signup_partener(request):
    try:
        city = request.session['location']
    except:
        city = None
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            if user:
                return render(request, 'register.html', {'error': 'Email Already Exist', 'location':city})
        except:
            user = None
        try:
            user = User.objects.get(username=username)
            if user:
                return render(request, 'register.html', {'error': 'Username Already Exist', 'location':city})
        except:
            user = None
        user = User.objects.create_user(email=email, username=username, password=password)
        user.save()
        profile = Profile(user=user, username=username, email=email,is_user=False, is_partener=True)
        profile.save()
        return redirect('signin')
    return render(request, 'partener-register.html', {'location':city})


@login_required(login_url="signin")
def logout_view(request):
    logout(request)
    return redirect("/")


def Profile_view(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    email=profile.email
    first_name=profile.first_name
    last_name=profile.last_name
    city=profile.city
    state=profile.state
    zipcode=profile.zipcode
    phone=profile.phone
    address=profile.address
    pic=profile.pic

    try:
        location = request.session['location']
    except:
        location = None
    context={"email":email,"first_name":first_name,"last_name":last_name,"city":city,"state":state,"zipcode":zipcode,"phone":phone,"address":address,"pic":pic, 'location':location}


    
    return render(request,'patient-profile.html',context)



def edit_profile(request):
    if request.method=="POST":
        username = request.user
        user = User.objects.get(username=username)
        profile=Profile.objects.get(user=username)

        profile.first_name=request.POST.get("first_name", "")
        profile.last_name=request.POST.get("last_name", "")
        profile.email=request.POST.get("email")
        profile.phone=request.POST.get("mob_no")
        profile.address=request.POST.get("address", "")
        profile.city=request.POST.get("city", "")
        profile.state=request.POST.get("state", "")
        profile.zipcode=request.POST.get("zipcode", "")
        profile.pic = request.FILES.get("image", "")

        profile.save()

        return redirect('/profile')



class RequestResetEmailView(View):
    
    def get(self, request):
        try:
            city = request.session['location']
        except:
            city = None
        return render(request, 'forget-password.html', {'location':city})

    def post(self, request):
        try:
            city = request.session['location']
        except:
            city = None
        email = request.POST['email']

        # if not validate_email(email):
        #     messages.error(request, 'Please enter a valid email')
        #     return render(request, 'template/forgot-password.html')


        user = User.objects.filter(email=email)

        print(user)

        if user.exists():

            print("No way")
            current_site = get_current_site(request)
            email_subject = '[Reset your Password]'
            message = render_to_string('reset-user-password.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )

            EmailThread(email_message).start()
        
        print("We have sent an email")

        # messages.success(
        #     request, 'We have sent you an email with instructions on how to reset your password')
        return render(request, 'forget-password.html', {'msg': 'Check your email for reset password link.', 'location':city})



class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                print("Invalid link request new one")
                return render(request, 'forget-password.html')

        except DjangoUnicodeDecodeError as identifier:
            print("Invalid link")
            return render(request, 'forget-password.html')

        return render(request, 'set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')


        if password != password2:
            print("Password not match")
            context['has_error'] = True

        if context['has_error'] == True:
            return render(request, 'set-new-password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            print(user)
            user.set_password(password)
          
            user.save()

            print("Password change succefully")

            return render(request,'login.html')

        except DjangoUnicodeDecodeError as identifier:
            print("Something went wrong")
            return render(request, 'set-new-password.html', context)

        return render(request, 'set-new-password.html', context)

    # return redirect("index")

@login_required(login_url="signin")
def dashboard(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    if is_partener:
        appointments = Appointment.objects.filter(partener=user).filter(status="Pending")
        appointments_count = len(appointments)
        patients_count = appointments_count
        doctors_count = len(Doctor.objects.filter(user=user))
        context = {"appointments":appointments, 'profile':profile, 'appointments_count':appointments_count, 'patients_count':patients_count, 'doctors_count':doctors_count}
        return render(request, 'dashboard/index.html', context)
    return redirect("index")

@login_required(login_url="signin")
def hospitals(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            pic = request.FILES['pic']
            hospital = Hospital(user=user, name=name, address=address, city=city, state=state, zipcode=zipcode, pic=pic)
            hospital.save()
            return redirect('hospitals')
        hospitals = Hospital.objects.filter(user=user)
        context = {'hospitals':hospitals}
        return render(request, 'dashboard/hospital.html', context)
    return redirect("index")

@login_required(login_url="signin")
def edit_hospital(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    hospital= Hospital.objects.get(id=id)
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            try:
                pic = request.FILES['pic']
            except:
                pic = None
            hospital.name = name
            hospital.address = address
            hospital.city = city
            hospital.state = state
            hospital.zipcode = zipcode
            if pic:
                hospital.pic = pic
            hospital.save()
            return redirect('hospitals')    
        hospitals = Hospital.objects.filter(user=user)
        context = {'hospitals':hospitals, 'hospital':hospital}
        return render(request, 'dashboard/hospital.html', context)
    return redirect("index")

@login_required(login_url="signin")
def delete_hospital(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    hospital= Hospital.objects.get(id=id)
    if is_partener:
        hospital.delete()
        return redirect("hospitals")
    return redirect("index")

@login_required(login_url="signin")
def ambulance(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            pic = request.FILES['pic']
            mobile = request.POST['mobile']
            ambulance = Ambulance(user=user, name=name, address=address, city=city, state=state, zipcode=zipcode, pic=pic, mobile=mobile)
            ambulance.save()
            return redirect('ambulance')
        all_ambulance = Ambulance.objects.filter(user=user)
        context = {'all':all_ambulance}
        return render(request, 'dashboard/ambulance.html', context)
    return redirect("index")

@login_required(login_url="signin")
def edit_ambulance(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    ambulance = Ambulance.objects.get(id=id)
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            mobile = request.POST['mobile']
            try:
                pic = request.FILES['pic']
            except:
                pic = None
            ambulance.name = name
            ambulance.address = address
            ambulance.city = city
            ambulance.state = state
            ambulance.zipcode = zipcode
            ambulance.mobile = mobile
            if pic:
                ambulance.pic = pic
            ambulance.save()
            return redirect('ambulance')    
        all_ambulance = Ambulance.objects.filter(user=user)
        context = {'all':all_ambulance, 'ambulance':ambulance}
        return render(request, 'dashboard/ambulance.html', context)
    return redirect("index")

@login_required(login_url="signin")
def delete_ambulance(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    ambulance = Ambulance.objects.get(id=id)
    if is_partener:
        ambulance.delete()
        return redirect("ambulance")
    return redirect("index")

@login_required(login_url="signin")
def medical_store(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            pic = request.FILES['pic']
            mobile = request.POST['mobile']
            medical = MedicalStore(user=user, name=name, address=address, city=city, state=state, zipcode=zipcode, pic=pic, mobile=mobile)
            medical.save()
            return redirect('medical-store')
        medicals = MedicalStore.objects.filter(user=user)
        context = {'medicals':medicals}
        return render(request, 'dashboard/medical-store.html', context)
    return redirect("index")

@login_required(login_url="signin")
def edit_medical_store(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    medical = MedicalStore.objects.get(id=id)
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            mobile = request.POST['mobile']
            try:
                pic = request.FILES['pic']
            except:
                pic = None
            medical.name = name
            medical.address = address
            medical.city = city
            medical.state = state
            medical.zipcode = zipcode
            medical.mobile = mobile
            if pic:
                medical.pic = pic
            medical.save()
            return redirect('medical-store')    
        medicals = MedicalStore.objects.filter(user=user)
        context = {'medicals':medicals, 'medical':medical}
        return render(request, 'dashboard/medical-store.html', context)
    return redirect("index")

@login_required(login_url="signin")
def delete_medical_store(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    medical = MedicalStore.objects.get(id=id)
    if is_partener:
        medical.delete()
        return redirect("medical-store")
    return redirect("index")

@login_required(login_url="signin")
def doctor(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            pic = request.FILES['pic']
            mobile = request.POST['mobile']
            email = request.POST['email']
            specialization = request.POST['specialization']
            doctor = Doctor(user=user, name=name, address=address, city=city, state=state, 
            specialization=specialization,zipcode=zipcode, pic=pic,email=email, mobile=mobile)
            doctor.save()
            return redirect('doctor')
        doctors = Doctor.objects.filter(user=user)
        context = {'doctors':doctors}
        return render(request, 'dashboard/doctors.html', context)
    return redirect("index")

@login_required(login_url="signin")
def edit_doctor(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    doctor = Doctor.objects.get(id=id)
    if is_partener:
        if request.method == "POST":
            name = request.POST['name']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            mobile = request.POST['mobile']
            email = request.POST['email']
            specialization = request.POST['specialization']
            try:
                pic = request.FILES['pic']
            except:
                pic = None
            doctor.name = name
            doctor.address = address
            doctor.city = city
            doctor.state = state
            doctor.zipcode = zipcode
            doctor.mobile = mobile
            doctor.email = email
            doctor.specialization = specialization
            if pic:
                doctor.pic = pic
            doctor.save()
            return redirect('doctor')    
        doctors = Doctor.objects.filter(user=user)
        context = {'doctors':doctors, 'doctor':doctor}
        return render(request, 'dashboard/doctors.html', context)
    return redirect("index")

@login_required(login_url="signin")
def delete_doctor(request, id):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    doctor = Doctor.objects.get(id=id)
    if is_partener:
        doctor.delete()
        return redirect("doctor")
    return redirect("index")

@login_required(login_url="signin")
def appointments(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    is_partener = profile.is_partener
    if is_partener:
        appointments = Appointment.objects.filter(partener=user)
        context={'is_partener':is_partener,'appointments':appointments}
        return render(request, "dashboard/appointment-list.html", context)
    return redirect("index")

def reverseGeocode(coordinates):
    result = rg.search(coordinates)
    print(result)
    city = result[0]["name"]
    return city

def setLocation(request):
    if request.method=="POST":
        lat = request.POST.get("lat", "21.1458")
        lng = request.POST.get("lng", "79.0882")
        coordinates = (lat, lng)
        city = reverseGeocode(coordinates)
        request.session['location'] = city
        return redirect("index")


def doctor_list(request):
    try:
        city = request.session['location']
    except:
        city = None
    doctor=Doctor.objects.all()
    return render(request,'doctorlist.html',{"doctor":doctor, 'location':city})

def hospital_list(request):
    try:
        city = request.session['location']
    except:
        city = None
    hospital=Hospital.objects.all()


    return render(request,'hospitallist.html',{"hospital":hospital, 'location':city})


def medical_store_list(request):
    try:
        city = request.session['location']
    except:
        city = None
    medical=MedicalStore.objects.all()

    return render(request,'medicallist.html',{"medical":medical, 'location':city})


def ambulance_list(request):
    try:
        city = request.session['location']
    except:
        city = None
    ambulance=Ambulance.objects.all()

    return render(request,'ambulancelist.html',{"ambulance":ambulance, 'location':city})





# search.views.py
from itertools import chain
from django.views.generic import ListView



class SearchView(ListView):
    template_name = 'search.html'
   
    def get_queryset(self):
        request = self.request
        query = request.GET.get('query', None)
        
        if query is not None:
           

            results = list(Hospital.objects.search(query))

            results += list(Doctor.objects.search(query))

            results += list(Ambulance.objects.search(query))

            results += list(MedicalStore.objects.search(query))

            results += list(Hospital.objects.filter(Q(name__icontains=query) | Q(address__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query)))
            results += list(Doctor.objects.filter(Q(name__icontains=query) | Q(address__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query)))
            results += list(Ambulance.objects.filter(Q(name__icontains=query) | Q(address__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query)))
            results += list(MedicalStore.objects.filter(Q(name__icontains=query) | Q(address__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query)))
            results = set(results)
            # combine querysets 
            queryset_chain = chain(
                results

            )        
            qs = sorted(queryset_chain, 
                        key=lambda instance: instance.pk, 
                        reverse=True)

            print(qs)
            self.count = len(qs) # since qs is actually a list
            return qs
        return Doctor.objects.none() # just an empty queryset as default



@login_required(login_url="signin")
def set_hospital_appointment(request, id):
    try:
        city = request.session['location']
    except:
        city = None
    try:
        user = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=user)
        is_partener = profile.is_partener
    except:
        user = None
        is_partener = None
    hospital = Hospital.objects.get(id=id)
    if request.method == "POST":
        datetime = request.POST["datetime"]
        category = request.POST["category"]
        date = str(datetime).split("T")[0]
        time = str(datetime).split("T")[1]
        appointment = Appointment(patient=user, hospital=hospital, partener=hospital.user, category=category,
        doctor=None, status="Pending", date=date, time=time)
        appointment.save()
        return redirect('user-appointments')
    context = {'hospital':hospital, "is_partener":is_partener, 'location':city}
    return render(request, 'booking.html', context)

@login_required(login_url="signin")
def set_doctor_appointment(request, id):
    try:
        city = request.session['location']
    except:
        city = None
    try:
        user = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=user)
        is_partener = profile.is_partener
    except:
        user = None
        is_partener = None
    doctor = Doctor.objects.get(id=id)
    if request.method == "POST":
        datetime = request.POST["datetime"]
        category = request.POST["category"]
        date = str(datetime).split("T")[0]
        time = str(datetime).split("T")[1]
        appointment = Appointment(patient=user, hospital=None, partener=doctor.user, category=category,
        doctor=doctor, status="Pending", date=date, time=time)
        appointment.save()
        return redirect('user-appointments')
    context = {'doctor':doctor, "is_partener":is_partener, 'location':city}
    return render(request, 'booking.html', context)

@login_required(login_url="signin")
def user_appointments(request):
    try:
        city = request.session['location']
    except:
        city = None
    try:
        user = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=user)
        is_partener = profile.is_partener
    except:
        user = None
        is_partener = None
    appointments = Appointment.objects.filter(patient=user)
    print(appointments)
    context = {'is_partener':is_partener, 'appointments':appointments, 'location':city}
    return render(request, "appointment-list.html", context)

@login_required(login_url="signin")
def text_message(request,appointment_id, partener_id, patient_id):
    try:
        secret_key = request.session['secret-key']
    except:
        secret_key = None
    if request.method == "POST":
        secret_key = request.POST['key']
    username = request.user
    appointment = Appointment.objects.get(id=appointment_id)
    if str(appointment.secret_key) == secret_key:
        request.session["secret-key"] = secret_key
        password = secret_key
    else:
        password = None
    user = User.objects.get(username=username)
    patient = User.objects.get(id=patient_id)
    partener = User.objects.get(id=partener_id)
    messages = list(Message.objects.filter(sender=partener))
    messages += list(Message.objects.filter(sender=patient))
    messages.sort(key = lambda message: message.id)
    context = {'user': user, 'partener':partener, 'patient':patient, 'messages':messages, 'password':password, 'appointment':appointment}
    return render(request, "chat.html", context)

@login_required(login_url="signin")
def send_message(request):
    username = request.user
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)   
    if request.method == "POST":
        text = request.POST["text"]
        sender_id = request.POST['sender']
        receiver_id = request.POST['receiver']
        partener_id = request.POST['partener']
        patient_id = request.POST['patient']
        appointment_id = request.POST['appointment']
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        message = Message(sender=sender, receiver=receiver, text=text)
        message.save()
        return redirect("text-message",appointment_id, partener_id, patient_id)
    return redirect("index")


from pyzoom import ZoomClient
from datetime import datetime as dt

def create_meeting_link(datetime):
    ZOOM_API_KEY = '8cAwrcPwRRKqKdx7WQhpNg'
    ZOOM_API_SECRET_KEY = 'egPIHwda7GRX9NVGWWqpCSmfl0dhEbheQdhv'
    client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET_KEY)
    meeting = client.meetings.create_meeting('DocTalk Online Doctor Consultancy', start_time=datetime,
    duration_min=60, password='not-secure')
    return meeting.join_url

@login_required(login_url="signin")
def accept_appointment(request, id):
    appointment = Appointment.objects.get(id=id)
    datetime = appointment.date+"T"+appointment.time
    if appointment.category == "Text Message":
        generate_link = get_current_site(request).domain + "/text-message/" + str(appointment.id) + "/" +str(appointment.partener.id) + "/" + str(appointment.patient.id)
        message = "Greetings from DocTalk.\n Your appointment has been approved.\nJoin this link on "+ appointment.date + " " + appointment.time + "\n"+ generate_link +"\nYour Secret Key is - "+ str(appointment.secret_key) +"\nDo not share with anyone.\nRegards, DocTalk."
        message2 = "You have a new appointment request.\nJoin this link on "+ appointment.date + " " + appointment.time + "\n"+ generate_link +"\nYour Secret Key is - "+ str(appointment.secret_key) +"\nDo not share with anyone.\nRegards, DocTalk."
    elif appointment.category == "Video Call":
        generate_link = create_meeting_link(datetime)
        message = "Greetings from DocTalk.\n Your appointment has been approved.\nJoin this link on "+ appointment.date + " " + appointment.time + "\n"+ generate_link +"\nRegards, DocTalk."
        message2 = "You have a new appointment request.\nJoin this link on "+ appointment.date + " " + appointment.time + "\n"+ generate_link +"\nRegards, DocTalk."
    else:
        generate_link = ""
        message = "Greetings from DocTalk.\n Your appointment has been approved."+ appointment.date + " " + appointment.time + "\nRegards, DocTalk."
        message2 = "You have a new appointment request on ."+ appointment.date + " " + appointment.time + "\nRegards, DocTalk."
    subject = "DocTalk Appointment Approved"
    receiver = appointment.patient.email
    sender = "doctalk2021.gladiators@gmail.com"
    send_mail(subject, message, sender, [receiver])
    subject2 = "DocTalk new appointment."
    receiver2 = [appointment.partener.email]
    if appointment.doctor:
        receiver2.append(appointment.doctor.email)
    send_mail(subject2, message2, sender, receiver2)
    appointment.status = "Approved"
    appointment.save()
    return redirect("dashboard")

@login_required(login_url="signin")
def reject_appointment(request, id):
    appointment = Appointment.objects.get(id=id)
    message = "Your appointment has been declined.\nSorry for inconvenience.\nBecause of too many requests, we are unable to process you request."
    subject = "DocTalk Appointment Approved"
    receiver = appointment.patient.email
    sender = "doctalk2021.gladiators@gmail.com"
    send_mail(subject, message, sender, [receiver])    
    appointment.status = "Declined"
    appointment.save()
    return redirect("dashboard")
    


@login_required(login_url="signin")
def doctor_profile(request,id):
    try:
        city = request.session['location']
    except:
        city = None
    doctor = Doctor.objects.get(id=id)
    
    username = request.user
    user = User.objects.get(username=username)


    if request.method=="POST":
        review_text=request.POST.get('review')

        review=Review(user=user,doctor=doctor,hospital=None,text=review_text)
        review.save()
        return redirect("doctor-profile",doctor.id)

    reviews=Review.objects.filter(doctor=doctor)
    return render(request,"doctor-profile.html",{"doctor":doctor,"reviews":reviews, 'location':city})



@login_required(login_url="signin")
def hospital_profile(request,id):
    try:
        city = request.session['location']
    except:
        city = None
    hospital = Hospital.objects.get(id=id)
    username = request.user
    user = User.objects.get(username=username)


    if request.method=="POST":
        review_text=request.POST.get('review')

        review=Review(user=user,doctor=None,hospital=hospital,text=review_text)
        review.save()
        return redirect("hospital-profile",hospital.id)

    reviews=Review.objects.filter(hospital=hospital)
   
    return render(request,"hospital-profile.html",{"hospital":hospital,"reviews":reviews, 'location':city})

