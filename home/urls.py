
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('signin', views.signin, name="signin"),
    path('user-signup', views.signup_user, name="user-signup"),
    path('partener-signup', views.signup_partener, name="partener-signup"),
    path('logout', views.logout_view, name='logout'),
    path('profile', views.Profile_view, name='profile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('forgot_password', views.RequestResetEmailView.as_view(), name='forgot_password'),
    path('set-new-password/<uidb64>/<token>',views.SetNewPasswordView.as_view(), name='set-new-password'),
    
    path('set-location', views.setLocation, name="set-location"),

    path('dashboard', views.dashboard, name="dashboard"),
    path('appointments', views.appointments, name="appointments"),
    path('hospitals', views.hospitals, name="hospitals"),
    path('edit-hospital/<str:id>', views.edit_hospital, name="edit-hospital"),
    path('delete-hospital/<str:id>', views.delete_hospital, name="delete-hospital"),

    path('ambulance', views.ambulance, name="ambulance"),
    path('edit-ambulance/<str:id>', views.edit_ambulance, name="edit-ambulance"),
    path('delete-ambulance/<str:id>', views.delete_ambulance, name="delete-ambulance"),

    path('medical-store', views.medical_store, name="medical-store"),
    path('edit-medical-store/<str:id>', views.edit_medical_store, name="edit-medical-store"),
    path('delete-medical-store/<str:id>', views.delete_medical_store, name="delete-medical-store"),

    path('doctor', views.doctor, name="doctor"),
    path('edit-doctor/<str:id>', views.edit_doctor, name="edit-doctor"),
    path('delete-doctor/<str:id>', views.delete_doctor, name="delete-doctor"),
    path('doctor_list', views.doctor_list, name='doctor_list'),
    path('hospital_list', views.hospital_list, name='hospital_list'),
    path('medical_list', views.medical_store_list, name='medical_list'),
    path('ambulance_list', views.ambulance_list, name='ambulance_list'),
    path('search_list', views.SearchView.as_view(), name='search_list'),

    path('set-hospital-appointment/<str:id>', views.set_hospital_appointment, name="set-hospital-appointment"),
    path('set-doctor-appointment/<str:id>', views.set_doctor_appointment, name="set-doctor-appointment"),
    path('user-appointments', views.user_appointments, name="user-appointments"),
    path('accept-appointment/<str:id>', views.accept_appointment, name="accept-appointment"),
    path('reject-appointment/<str:id>', views.reject_appointment, name="reject-appointment"),

    path('text-message/<str:appointment_id>/<str:partener_id>/<str:patient_id>', views.text_message, name="text-message"),
    path('send-message', views.send_message, name="send-message"),
    path('doctor-profile/<str:id>', views.doctor_profile, name="doctor-profile"),
    path('hospital-profile/<str:id>', views.hospital_profile, name="hospital-profile"),
]

