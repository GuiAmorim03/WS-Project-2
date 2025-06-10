"""
URL configuration for ws_project_1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import *
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage


urlpatterns = [
    path('admin/', admin.site.urls),
    path("player/<str:player_id>", player_detail, name="player"),
    path("club/<str:club_id>", club_detail, name="club"),
    path("players", players, name="players"),
    path("clubs", clubs, name="clubs"),
    path("graph", graph_view, name="graph"),
    path("", dashboard, name="dashboard"),
    path("player/<str:player_id>/add_club/", add_club_to_player, name="add_club"),
    path("player/<str:player_id>/add_position/", add_position_to_player, name="add_position"),
    path("player-connection/", player_connection_checker, name="player_connection"),
    path('players/<str:player_id>/delete/', delete_player_view, name='delete_player'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico')), name='favicon'),
    path('stadium/<str:stadium_id>', stadium_detail, name='stadium'),
]
