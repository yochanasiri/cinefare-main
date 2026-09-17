from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from movies.models import ads,Movie,movieComment,movie_rating,theatre,booked_seats,location
from math import ceil
import json
import razorpay
from razorpay.errors import SignatureVerificationError
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
current_date = timezone.localdate()
current_time = timezone.localtime(timezone.now()).time()

TICKET_PRICE = 250
HOLD_MINUTES = 8


def release_expired_holds():
    cutoff = timezone.now() - timedelta(minutes=HOLD_MINUTES)
    booked_seats.objects.filter(status='HOLD', created_at__lt=cutoff).update(status='RELEASED')


def seats_url(city, movie_id, date, tname, show):
    return f"/{city}/movie/{movie_id}/{date}/{tname}/{show}/"


def razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Pages
def locationPage(request):
    return render(request,'location.html')

def HomePage(request,city):
    req_user = request.user
    leng = 0
    if req_user.is_authenticated:
        booked = booked_seats.objects.filter(user=req_user,date__gte=current_date,status='BOOKED').order_by('date')
        leng = len(booked)
    else:
        booked = None

    objects = ads.objects.all()
    no = len(objects)
    req_loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(location=req_loc)
    movies = Movie.objects.filter(theatres__in=theatres).distinct()
    telugu_movies = Movie.objects.filter(theatres__in=theatres, language__contains='Telugu').distinct()
    tamil_movies = Movie.objects.filter(theatres__in=theatres, language__contains='Tamil').distinct()
    hindi_movies = Movie.objects.filter(theatres__in=theatres, language__contains='Hindi').distinct()
    params={'movies':movies, 'ads':objects, 'noads':range(no),'telugu_movies':telugu_movies,'tamil_movies':tamil_movies, 'hindi_movies':hindi_movies,'city':city,'booked':booked,'len':leng}
    return render(request,'home.html',params)

def allmovies(request, city):
    req_loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(location=req_loc)
    objects = ads.objects.all()
    movies = Movie.objects.filter(theatres__in=theatres).distinct()
    no = len(objects)
    lang_filter = "Language"
    gen_filter = "Genre"
    params={'movies':movies, 'ads':objects, 'noads':range(no),'city':city,'lang_filter':lang_filter,'gen_filter':gen_filter}
    return render(request,'allmovies.html',params)

def genlang(request, city, gen, lang):
    req_loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(location=req_loc)
    objects = ads.objects.all()
    if gen!="gen":
        if lang!="lang":
            movies = Movie.objects.filter(theatres__in=theatres,genre__contains=gen, language__contains=lang).distinct()
        else:
            movies = Movie.objects.filter(theatres__in=theatres,genre__contains=gen).distinct()
    else:
        movies = Movie.objects.filter(theatres__in=theatres,language__contains=lang).distinct()

    no = len(objects)
    lang_filter = lang
    gen_filter = gen
    params={'movies':movies, 'ads':objects, 'noads':range(no),'city':city,'lang_filter':lang_filter,'gen_filter':gen_filter}
    return render(request,'allmovies.html',params)

def movie(request, id, city):
    movie = Movie.objects.get(movie_id=id)
    try:
        rate = movie_rating.objects.get(movie=movie)
    except movie_rating.DoesNotExist:
        rate = movie_rating(movie=movie, rating=0, numratings=0)
        rate.save()
    comments = movieComment.objects.filter(movie=movie)
    genres = movie.genre.split(',')
    liked = Movie.objects.filter(genre__icontains=genres[0].strip()).exclude(movie_id=id)
    for genre in genres[1:]:
        liked = liked | Movie.objects.filter(genre__icontains=genre.strip()).exclude(movie_id=id)
    params = {'movie': movie, 'liked': liked, 'comments':comments,'user':request.user,'rate':rate,'city':city,'date':current_date}
    return render(request, 'movie.html', params)

def search_movies(request, city):
    if request.method == "POST":
        search = request.POST['search_movies']
        try:
            movie = Movie.objects.get(movie_title__iexact=search)
            return redirect(f"/{city}/movie/{movie.movie_id}/")
        except Movie.DoesNotExist:
            movies = Movie.objects.filter(movie_title__contains=search)
            no = len(movies)
            if no == 0:
                messages.error(request, "No Movies are found!!")
                return redirect(f"/{city}/")
            params = {'movies': movies, 'nomovies': range(no),'city':city}
            return render(request, 'search.html', params)
    return render(request, 'search.html')

def postComment(request,city):
    if request.method =="POST":
        comment = request.POST.get("comment")
        user = request.user
        movie_id = request.POST.get("movie_id")
        movie = Movie.objects.get(movie_id=movie_id)
        
        comment = movieComment(comment=comment, user=user, movie=movie)
        comment.save()
        messages.success(request,"Your comment has been posted successfully!")
    return redirect(f"/{city}/movie/{movie.movie_id}/")

def ratenow(request,city):
    if request.method == "POST":
        user_rate = request.POST.get("user_rate")
        movie_id = request.POST.get("movie_id")
        movie = Movie.objects.get(movie_id=movie_id)
        try:
            rating_obj = movie_rating.objects.get(movie=movie)
        except movie_rating.DoesNotExist:
            rating_obj = movie_rating(movie=movie, rating=0, numratings=0)
            rating_obj.save()

        rating_obj.numratings += 1
        rating_obj.rating = (rating_obj.rating * (rating_obj.numratings - 1) + 6-int(user_rate)) / rating_obj.numratings
        rating_obj.save()

        messages.success(request, "You rated successfully!")

    return redirect(f"/{city}/movie/{movie.movie_id}/")

def alltheatres(request, id, city,date):
    movie = Movie.objects.get(movie_id=id)
    loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(movies=movie,location=loc)
    tomorrow = current_date + timezone.timedelta(days=1)
    dat = current_date + timezone.timedelta(days=2)
    time_now = timezone.localtime(timezone.now())
    first_show = datetime.strptime('11:00:00', '%H:%M:%S').time()
    second_show = datetime.strptime('14:30:00', '%H:%M:%S').time()
    third_show = datetime.strptime('18:00:00', '%H:%M:%S').time()
    last_show = datetime.strptime('21:00:00', '%H:%M:%S').time()
    c1=0
    c2=0
    c3=0
    c4=0
    date = datetime.strptime(date, '%b. %d, %Y')
    if date.date() == current_date:
        if current_time>first_show:
            c1=1
        if current_time>second_show:
            c2=1
        if current_time>third_show:
            c3=1
        if current_time>last_show:
            c4=1
    date = date.date()
    params = {'movie':movie, 'theatres':theatres,'city':city,'date':current_date,'tom':tomorrow,'dat':dat,'sel':date,'time':time_now,'c1':c1,'c2':c2,'c3':c3,'c4':c4}
    return render(request,'theatres.html', params)

def seats(request, id, show, tname, city, date):
    movie = Movie.objects.get(movie_id=id)
    t = theatre.objects.get(theatre_name=tname)
    show = show
    date = datetime.strptime(date, '%b. %d, %Y')
    release_expired_holds()
    bs = booked_seats.objects.filter(theatre=t, show=show, movie=movie,date=date.date()).exclude(status='RELEASED').values_list('seat_no', flat=True)
    bs = [item for sublist in [elem.split(',') if ',' in elem else [elem] for elem in bs] for item in sublist]
    params = {
        'movie': movie,
        'theatre': t,
        'date':date.date(),
        'show': show,
        'booked_seats':bs,
        'city':city,
    }
    return render(request, 'seats.html', params)

def reserve_seats(request, id, show, tname, city, date):
    if request.method != 'POST':
        return redirect(seats_url(city, id, date, tname, show))
    if not request.user.is_authenticated:
        messages.error(request, "Please login to book tickets!")
        return redirect(seats_url(city, id, date, tname, show))

    try:
        selected = json.loads(request.POST.get('selected_seats', '[]'))
    except json.JSONDecodeError:
        selected = []
    selected = [s.strip() for s in selected if s.strip()]
    if not selected:
        messages.error(request, "Please select at least one seat!")
        return redirect(seats_url(city, id, date, tname, show))

    movie = Movie.objects.get(movie_id=id)
    t = theatre.objects.get(theatre_name=tname)
    show_date = datetime.strptime(date, '%b. %d, %Y').date()
    release_expired_holds()

    with transaction.atomic():
        taken = set()
        blocking = booked_seats.objects.filter(theatre=t, show=show, movie=movie, date=show_date).exclude(status='RELEASED').values_list('seat_no', flat=True)
        for seat_str in blocking:
            taken.update(seat_str.split(','))
        clash = sorted(set(selected) & taken)
        if clash:
            messages.error(request, f"Seat(s) {', '.join(clash)} were just taken by someone else. Please pick different seats.")
            return redirect(seats_url(city, id, date, tname, show))
        booking = booked_seats(seat_no=','.join(selected), theatre=t, show=show, movie=movie,
                               user=request.user, date=show_date, status='HOLD')
        booking.save()

    amount = len(selected) * TICKET_PRICE * 100  # paise
    try:
        order = razorpay_client().order.create(data={
            "amount": amount,
            "currency": "INR",
            "receipt": f"booking_{booking.pk}",
        })
    except Exception:
        booking.status = 'RELEASED'
        booking.save()
        messages.error(request, "Could not start the payment. Please try again.")
        return redirect(seats_url(city, id, date, tname, show))

    booking.razorpay_order_id = order['id']
    booking.save()
    return redirect(f"/{city}/payment/{booking.pk}/")

def generate_pdf(request,city,book):
    if not request.user.is_authenticated:
        return redirect(f'/{city}/')
    bookk = book.split()
    booking = booked_seats.objects.filter(seat_no=bookk[0], user=request.user, status='BOOKED').order_by('-pk').first()
    if booking is None:
        return HttpResponse("Booking not found", status=404)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cinefare_booking.pdf"'
    # Create a PDF object
    pdf = canvas.Canvas(response, pagesize=letter)
    # Create a paragraph style
    style = ParagraphStyle(
        'my_custom_style',
        fontSize=12,
        leading=16
    )
    text_content = [
        Paragraph(f"*Movie Tickect Details*", style),
        Paragraph(f"<b>Id:</b> 346323456", style),
        Paragraph(f"<b>Movie:</b> {booking.movie}", style),
        Paragraph(f"<b>Date:</b> {booking.date}", style),
        Paragraph(f"<b>Show:</b> {booking.show}", style),
        Paragraph(f"<b>Theatre:</b> {booking.theatre}", style),
        Paragraph(f"<b>Seats:</b> {bookk[0]}", style),
    ]

    y_coordinate = 750
    for text_object in text_content:
        text_object.wrapOn(pdf, 400, 100)
        text_object.drawOn(pdf, 100, y_coordinate)
        y_coordinate -= 20
    # # Draw an image on the PDF
    image_path = 'static/images.png'
    image = ImageReader(image_path)
    pdf.drawImage(image, 100, 500, width=150, height=150)

    pdf.save()

    return response      

def payment(request, city, booking_id):
    if not request.user.is_authenticated:
        return redirect(f'/{city}/')
    try:
        booking = booked_seats.objects.get(pk=booking_id, user=request.user)
    except booked_seats.DoesNotExist:
        return redirect(f'/{city}/')

    release_expired_holds()
    booking.refresh_from_db()

    seat_list = booking.seat_no.split(',')
    amount = len(seat_list) * TICKET_PRICE * 100
    back_url = seats_url(city, booking.movie.movie_id, booking.date.strftime('%b. %d, %Y'),
                         booking.theatre.theatre_name, booking.show.strftime('%H:%M'))
    if booking.status == 'BOOKED':
        state = 'success'
    elif booking.status == 'RELEASED':
        state = 'gone'
    else:
        state = 'pay'
    params = {
        'city': city,
        'booking': booking,
        'state': state,
        'amount': amount,
        'amount_rupees': amount // 100,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'back_url': back_url,
        'hold_minutes': HOLD_MINUTES,
    }
    return render(request, 'payment.html', params)


def payment_verify(request, city, booking_id):
    if request.method != 'POST':
        return redirect(f'/{city}/payment/{booking_id}/')
    if not request.user.is_authenticated:
        return redirect(f'/{city}/')
    try:
        booking = booked_seats.objects.get(pk=booking_id, user=request.user)
    except booked_seats.DoesNotExist:
        return redirect(f'/{city}/')

    params = {
        'razorpay_order_id': request.POST.get('razorpay_order_id', ''),
        'razorpay_payment_id': request.POST.get('razorpay_payment_id', ''),
        'razorpay_signature': request.POST.get('razorpay_signature', ''),
    }
    if params['razorpay_order_id'] != booking.razorpay_order_id:
        messages.error(request, "This payment does not match the booking.")
        return redirect(f'/{city}/payment/{booking_id}/')
    try:
        razorpay_client().utility.verify_payment_signature(params)
    except SignatureVerificationError:
        messages.error(request, "Payment verification failed. If money was deducted it will be refunded automatically.")
        return redirect(f'/{city}/payment/{booking_id}/')

    with transaction.atomic():
        taken = set()
        others = booked_seats.objects.filter(theatre=booking.theatre, show=booking.show,
                                             movie=booking.movie, date=booking.date
                                             ).exclude(pk=booking.pk).exclude(status='RELEASED'
                                             ).values_list('seat_no', flat=True)
        for seat_str in others:
            taken.update(seat_str.split(','))
        if set(booking.seat_no.split(',')) & taken:
            messages.error(request, "Payment received, but your seat hold expired and the seats were taken. Please contact support for a refund.")
            return redirect(f'/{city}/payment/{booking_id}/')
        booking.status = 'BOOKED'
        booking.save()
    return redirect(f'/{city}/payment/{booking_id}/')


def payment_cancel(request, city, booking_id):
    if not request.user.is_authenticated:
        return redirect(f'/{city}/')
    try:
        booking = booked_seats.objects.get(pk=booking_id, user=request.user)
    except booked_seats.DoesNotExist:
        return redirect(f'/{city}/')

    back_url = seats_url(city, booking.movie.movie_id, booking.date.strftime('%b. %d, %Y'),
                         booking.theatre.theatre_name, booking.show.strftime('%H:%M'))
    if booking.status == 'HOLD':
        booking.status = 'RELEASED'
        booking.save()
        messages.success(request, "Payment cancelled — your seats have been released.")
    return redirect(back_url)

# Authentiacation
def Signup(request, city):
    if request.method == "POST":
        loc = city
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        mobileno = request.POST['mobileno']
        email = request.POST['email']
        pass1 = request.POST['pass0']
        pass2 = request.POST['pass2']
        user=User.objects.filter(username=username)
        if user.exists():
            messages.error(request,"Username already exists! Try another")
            return redirect(f'/{loc}/')
        if pass1!=pass2:
            messages.error(request,"Please enter same password in both!!")
            return redirect(f'/{loc}/')
        myuser = User.objects.create_user(username=username,email=email,password=pass1) 
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.mobileno = mobileno
        myuser.save()
        messages.success(request,"Your Cinefare account has been Successfully Created!!")
        return redirect(f'/{loc}/')
    return render(request,'signin.html')

def edit(request,city):
    if request.method == "POST":
        loc = city
        fname = request.POST['fname']
        lname = request.POST['lname']
        mobileno = request.POST['mobileno']
        email = request.POST['email']
        myuser=request.user
        if fname!="":
            myuser.first_name = fname
        if lname!="":
            myuser.last_name = lname
        if mobileno!="":
            myuser.mobileno = mobileno
        if email!="":
            myuser.email = email
        myuser.save()
        messages.success(request,"Changes saved successfully!!")
        return redirect(f'/{loc}/')
    return redirect(f'/{loc}/')

def Login(request, city):
    if request.method == "POST":
        loginusername = request.POST['username']
        loginpassword = request.POST['pass1']
        loc = city
        user = authenticate(username=loginusername,password=loginpassword)
        if user is not None:
            login(request,user)
            messages.success(request,"Succesfully logged in")
            return redirect(f'/{loc}/')
        else:
            messages.error(request,"Invalid Credentials!!")
            return redirect(f'/{loc}/')    
    return render(request,'signin.html',{'city':city})

def Logout(request,city):
    loc = city
    logout(request)
    messages.success(request,"Successfully Logged out!!")
    return redirect(f'/{loc}/')
