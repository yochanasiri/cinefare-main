from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone
class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=50, blank=False, null=False)
    genre = models.CharField(max_length=50)
    desc = models.TextField()
    trailer = models.URLField()
    language = models.CharField(max_length=50,null=True)
    # cast and crew
    hero_name = models.CharField(max_length=50,blank=True,null=True)
    heroine_name = models.CharField(max_length=50,blank=True,null=True)
    director_name = models.CharField(max_length=50,blank=True,null=True)
    producer_name = models.CharField(max_length=50,blank=True,null=True)
    sideactor_name = models.CharField(max_length=50,blank=True,null=True)
    movie_poster = models.URLField()
    heroimg = models.URLField()
    heroineimg = models.URLField()
    directorimg = models.URLField()
    producerimg = models.URLField()
    sideactorimg = models.URLField()
    bgi = models.URLField()

    def __str__(self):
        return self.movie_title

class ads(models.Model):
    ad_name = models.CharField(max_length=50,primary_key=True)
    adpic = models.URLField()

    def __str__(self):
        return self.ad_name

class movieComment(models.Model):
    sno = models.AutoField(primary_key=True)
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.comment[0:13]+"... by " + self.user.username

class movie_rating(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1,default=0)
    numratings = models.IntegerField()
    
    def __str__(self):
        return "rating of "+ self.movie.movie_title
    
class theatre(models.Model):
    theatre_id = models.AutoField(primary_key=True)
    theatre_name = models.CharField(max_length=50)
    theatre_map = models.URLField()
    movies = models.ManyToManyField('Movie', related_name='theatres')
    location = models.ForeignKey('location', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.theatre_name
    
class booked_seats(models.Model):
    # HOLD     - seats held while the user is paying (expires after a few minutes)
    # BOOKED   - payment verified, booking confirmed
    # RELEASED - hold cancelled/expired or payment failed; seats available again
    STATUS_CHOICES = [('HOLD', 'HOLD'), ('BOOKED', 'BOOKED'), ('RELEASED', 'RELEASED')]

    seat_no = models.CharField(max_length=100)
    theatre = models.ForeignKey(theatre,on_delete=models.CASCADE)
    show = models.TimeField()
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    date = models.DateField(default=timezone.now)
    # default BOOKED so pre-existing rows and admin-created rows count as confirmed;
    # the checkout flow always creates rows with status='HOLD' explicitly
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='BOOKED')
    razorpay_order_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.seat_no + " in " +self.theatre.theatre_name+" for "+self.movie.movie_title +" by "+self.user.username

class location(models.Model):
    location = models.CharField(max_length=50)

    def __str__(self):
        return self.location
    

