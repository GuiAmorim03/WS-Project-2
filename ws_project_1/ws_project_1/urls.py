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


urlpatterns = [
    path('admin/', admin.site.urls),
    path("player/<path:player_id>", player_detail, name="player"),
    path("club/<path:club_id>", club_detail, name="team"),
    path("players", players, name="players"),
    path("clubs", clubs, name="clubs"),
    path("graph", graph_view, name="graph"),
    path("", dashboard, name="dashboard"),
]
