from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('post/', views.post_recipe, name='post_recipe'), 
    path('favorites/', views.favorites_view, name='favorites'),
     path('shopping-list/', views.shopping_list, name='shopping_list'),
    path('add-to-shopping-list/<int:ingredient_id>/', views.add_to_shopping_list, name='add_to_shopping_list'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:recipe_id>/favorite-toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('recipe/<int:recipe_id>/comment/', views.add_comment, name='add_comment'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
     path('shopping/delete/<int:item_id>/', views.delete_shopping_item, name='delete_shopping_item'),
]
