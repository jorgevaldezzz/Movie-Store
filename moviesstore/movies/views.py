from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

def index(request):
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = Movie.objects.all()
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
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
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def create_rating(request, id):
    if request.method == 'POST':
        movie = Movie.objects.get(id=id)
        rating_value = request.POST.get('rating')

        allowed_values = ['1.0','1.5','2.0','2.5','3.0','3.5','4.0','4.5','5.0']
        if rating_value not in allowed_values:
            return redirect('movies.show', id=id)

        rating, created = Rating.objects.get_or_create(
            movie=movie,
            user=request.user
        )

        rating.rating = rating_value
        rating.save()

    return redirect('movies.show', id=id)

@login_required
def edit_rating(request, id):
    rating = get_object_or_404(Rating, movie_id=id, user=request.user)

    if request.method == 'POST':
        rating.rating = request.POST['rating']
        rating.save()
        return redirect('movies.show', id=id)

    return render(request, 'movies/edit_rating.html', {'rating': rating})

@login_required
def delete_rating(request, id):
    rating = get_object_or_404(Rating, movie_id=id, user=request.user)
    rating.delete()
    return redirect('movies.show', id=id)