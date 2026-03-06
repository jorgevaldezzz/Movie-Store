import csv
import json
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
import django_countries
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.core.serializers.json import DjangoJSONEncoder

ALLOWED_RATING_VALUES = {'1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'}

ALLOWED_RATING_VALUES = {'1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'}


def index(request):
    template_data = {}
    template_data['title'] = 'Movies'
    search = request.GET.get('search')

    if search:
        movies = Movie.objects.filter(name__icontains=search)
    else:
        movies = Movie.objects.all()

    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})


def show(request, id):
    movie = get_object_or_404(Movie, id=id)
    reviews = Review.objects.filter(movie=movie)
    ratings = Rating.objects.filter(movie=movie)

    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(movie=movie, user=request.user).first()

    template_data = {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_rating': user_rating
    }

    return render(request, 'movies/show.html', {'template_data': template_data})


@login_required
def create_review(request, id):
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            movie = get_object_or_404(Movie, id=id)
            review = Review()
            review.comment = comment
            review.movie = movie
            review.user = request.user
            review.save()

    return redirect('movies.show', id=id)


@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {
            'title': 'Edit Review',
            'review': review
        }
        return render(request, 'movies/edit_review.html', {'template_data': template_data})

    elif request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            review.comment = comment
            review.save()

    return redirect('movies.show', id=id)


@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


@login_required
def create_rating(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        rating_value = request.POST.get('rating')

        if rating_value not in ALLOWED_RATING_VALUES:
            return redirect('movies.show', id=id)

        rating, created = Rating.objects.get_or_create(
            movie=movie,
            user=request.user,
            defaults={'rating': rating_value}
        )

        if not created:
            rating.rating = rating_value
            rating.save()

    return redirect('movies.show', id=id)


@login_required
def edit_rating(request, id):
    rating = get_object_or_404(Rating, movie_id=id, user=request.user)

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        if rating_value in ALLOWED_RATING_VALUES:
            rating.rating = rating_value
            rating.save()
        return redirect('movies.show', id=id)

    return render(request, 'movies/edit_rating.html', {'rating': rating})


@login_required
def delete_rating(request, id):
    rating = get_object_or_404(Rating, movie_id=id, user=request.user)
    rating.delete()
    return redirect('movies.show', id=id)


def map_view(request):
    # country_code -> {movie_id, movie_name, avg_rating, rating_count}                                                                                                                                                                                                     
    top_per_country = {}                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                             
    rows = (                                                                                                                                                                                                                                                               
        Rating.objects                                                                                                                                                                                                                                                     
        .exclude(user__profile__region__isnull=True)                                                                                                                                                                                                                       
        .values("user__profile__region", "movie__id", "movie__name", "movie__image")                                                                                                                                                                                       
        .annotate(avg_rating=Avg("rating"), rating_count=Count("id"))                                                                                                                                                                                                      
    )                                                                                                                                                                                                                                                                      
     
     # lets make a new map which holds top 5 movies per country                                                                                                                                                                                                                                                                      
    for row in rows:                                                                                                                                                                                                                                                       
        country = row["user__profile__region"]                                                                                                                                                                                                                             
        current = top_per_country.get(country)                                                                                                                                                                                                                             
        if current is None:                                                                                                                                                                                                                                                
            top_per_country[country] = [row]                                                                                                                                                                                                                                 
            continue  
        
        # we want to keep top 5 movies per country, so we will add the current movie to the list and then sort the list by avg_rating and rating_count and keep only top 5                                                                                                                                                                                                                                                        
        top_per_country[country].append(row)
        top_per_country[country].sort(key=lambda x: (x["avg_rating"], x["rating_count"]), reverse=True)
        top_per_country[country] = top_per_country[country][:5]                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                           
    # Debug print removed to avoid noisy output in production.
            
    # use countries.csv to add lat long points 
    csv_path = Path(__file__).resolve().parent / "data" / "countries.csv"  
    iso_to_latlng = {}                                                                                                                                                                                                                                                     
    with csv_path.open(newline="", encoding="utf-8") as f:                                                                                                                                                                                                                 
        reader = csv.DictReader(f)                                                                                                                                                                                                                                         
        for r in reader:                                                                                                                                                                                                                                                   
          iso_to_latlng[r["ISO"]] = {                                                                                                                                                                                                                                    
              "lat": float(r["latitude"]),                                                                                                                                                                                                                               
              "lng": float(r["longitude"]),                                                                                                                                                                                                                              
          }                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                         
    map_points = []
    for iso, movielist in top_per_country.items():
        latlng = iso_to_latlng.get(iso)
        if not latlng:
            continue
        for row in movielist:
            image_path = row["movie__image"]
            image_url = f"{settings.MEDIA_URL}{image_path}" if image_path else ""
            row["movie__image"] = image_url
        map_points.append({
            "country": iso,
            "movies": top_per_country[iso],
            "lat": latlng["lat"],
            "lng": latlng["lng"],
        })
    print("MAP POINTS", map_points)  # Debug print to verify map points data structure
    template_data = {
        'title': 'Movie Map',
        'popMoviesToCountryMap': top_per_country,
        'map_points_json': json.dumps(map_points, cls=DjangoJSONEncoder)
    }
    return render(request, 'movies/map.html', {'template_data': template_data})
