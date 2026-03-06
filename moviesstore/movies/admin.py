from django.contrib import admin
from .models import Movie, Review
from django.db.models import Count
from django.urls import path
from django.shortcuts import render


# Register your models here.

from .models import Movie, Rating, Review
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Rating)

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
    

from django.contrib.admin import AdminSite
original_get_urls = AdminSite.get_urls

def patched_get_urls(self):
    custom = [
        path('top-commenter/', self.admin_view(self.top_commenter_view), name='top_commenter'),
    ]
    return custom + original_get_urls(self)

AdminSite.get_urls = patched_get_urls
AdminSite.top_commenter_view = TopCommenterAdmin.top_commenter_view

        
        
