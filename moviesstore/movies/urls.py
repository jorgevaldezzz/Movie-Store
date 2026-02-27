from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('<int:id>/rating/create/', views.create_rating, name='movies.create_rating'),
    path('<int:id>/rating/edit/', views.edit_rating, name='movies.edit_rating'),
    path('<int:id>/rating/delete/', views.delete_rating, name='movies.delete_rating'),
]