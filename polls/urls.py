from django.urls import path

from . import views


urlpatterns = [
    path('', views.getinfo_All, name='getinfo_All'),
    path('res', views.getreservation_All, name='getreservation_All'),
    path('login', views.login, name='login'),
    path('reservepost', views.reservepost, name='reservepost'),
    path('count_shift_post', views.count_shift_post, name='count_shift_post'),
    path('reservepost_cancel', views.reservepost_cancel, name='reservepost_cancel'),
    path('myreservations', views.myreservations, name='myreservationsl'),
    path('valid_reservation', views.valid_reservation, name='valid_reservation'),
    path('query_about_cancel', views.query_about_cancel, name='query_about_cancel'),
    path('cancel_requests_for_admin', views.cancel_requests_for_admin, name='cancel_requests_for_admin'),
    path('getALL_reservsrtionCancel', views.getALL_reservsrtionCancel, name='getALL_reservsrtionCancel'),
    path('accept_button', views.accept_button, name='accept_button'),
]