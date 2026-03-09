from django.contrib import admin
from .models import Movie, Review
from django.db.models import Count, Sum
from django.urls import path
from django.shortcuts import render
from cart.models import Item


# Register your models here.

from .models import Movie, Rating, Review
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Rating)

class TopPurchaserAdmin:
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('top-purchaser/', self.admin_view(self.top_purchaser_view), name='top-purchaser'),
        ]
        return custom_urls + urls
    
    def top_purchaser_view(self, request):
        leaderboard = (Item.objects.values('order__user__id', 'order__user__username').annotate(purchases=Sum('quantity')).order_by('-purchases'))
        
        context = {
            **self.each_context(request), 
            'title': 'Top Purchaser', 
            'top_purchaser': leaderboard.first(), 
            'leaderboard': list(leaderboard), 
        }
        return render(request, 'admin/top_purchaser.html', context)

class TopCommenterAdmin:
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('top-commenter/', self.admin_view(self.top_commenter_view), name='top-commenter'),
        ]
        return custom_urls + urls
    
    def top_commenter_view(self, request):
        leaderboard = (Review.objects.values('user__id', 'user__username', 'user__email').annotate(
            comments_made = Count('id')).order_by('-comments_made'))
        
        context = {
            **self.each_context(request), 
            'title': 'Top Commenter', 
            'top_user': leaderboard.first(), 
            'leaderboard': list(leaderboard), 
        }
        return render(request, 'admin/top_commenter.html', context)
    
class TopMovieAdmin:
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('top-movie/', self.admin_view(self.top_movie_view), name='top_movie'),
        ]
        return custom_urls + urls

    def top_movie_view(self, request):
        leaderboard = (Movie.objects.annotate(
            purchases=Sum('item__quantity')).values('name','purchases').order_by('-purchases'))

        context = {
            **self.each_context(request),
            'title': 'Top Movie',
            'top_movie': leaderboard.first(),
            'leaderboard': list(leaderboard),
        }
        return render(request, 'admin/top_movie.html', context)
from django.contrib.admin import AdminSite
original_get_urls = AdminSite.get_urls

def patched_get_urls(self):
    custom = [
        path('top-commenter/', self.admin_view(self.top_commenter_view), name='top_commenter'),
        path('top-movie/', self.admin_view(self.top_movie_view), name='top_movie'),
        path('top-purchaser/', self.admin_view(self.top_purchaser_view), name='top_purchaser'),
    ]
    return custom + original_get_urls(self)

AdminSite.get_urls = patched_get_urls
AdminSite.top_commenter_view = TopCommenterAdmin.top_commenter_view
AdminSite.top_movie_view = TopMovieAdmin.top_movie_view
AdminSite.top_purchaser_view = TopPurchaserAdmin.top_purchaser_view

        
        
