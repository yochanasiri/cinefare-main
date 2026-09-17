from django.contrib import admin
from .models import Movie,ads,movieComment,movie_rating,theatre,booked_seats,location

admin.site.register((Movie,ads,movieComment,movie_rating,theatre,booked_seats,location  ))
