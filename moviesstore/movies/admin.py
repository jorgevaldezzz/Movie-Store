from django.contrib import admin
from .models import Movie, Rating, Review
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Rating)

# Register your models here.
