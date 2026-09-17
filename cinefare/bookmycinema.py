from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Cinefare admin"
admin.site.site_title = "Cinefare"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.locationPage, name="location"),
    path('<str:city>/', views.HomePage, name="home"),
    path('<str:city>/search_movies/', views.search_movies, name="search_movies"),
    path('<str:city>/signup/', views.Signup, name="Signup"),
    path('<str:city>/edit/', views.edit, name="edit"),
    path('<str:city>/login/', views.Login, name="Login"),
    path('<str:city>/logout/', views.Logout, name="Logout"),
    path('<str:city>/<str:book>/generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('<str:city>/allmovies/', views.allmovies, name="allmovies"),
    path('<str:city>/movie/<int:id>/', views.movie, name="movie"),
    path('<str:city>/postComment/', views.postComment, name="postComment"),
    path('<str:city>/ratenow/', views.ratenow, name="ratenow"),
    path('<str:city>/movie/<int:id>/alltheatres/<str:date>/', views.alltheatres, name="alltheatres"),
    path('<str:city>/movie/<int:id>/<str:date>/<str:tname>/<str:show>/', views.seats, name="seats"),
    path('<str:city>/movie/<int:id>/<str:date>/<str:tname>/<str:show>/reserve_seats/', views.reserve_seats, name="reserve_seats"),
    path('<str:city>/payment/<int:booking_id>/', views.payment, name="payment"),
    path('<str:city>/payment/<int:booking_id>/verify/', views.payment_verify, name="payment_verify"),
    path('<str:city>/payment/<int:booking_id>/cancel/', views.payment_cancel, name="payment_cancel"),
    path('<str:city>/<str:gen>/<str:lang>/', views.genlang, name="genlang"),

] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
