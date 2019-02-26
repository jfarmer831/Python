from django.urls import path

from . import views

urlpatterns = [
    path('weather', views.weather_data, name='weather'),
    path('movies', views.movie_data, name='movies'),
    path('news', views.news_data, name='news'),
    path('events', views.events_data, name='events'),
    path('nasa', views.nasa_data, name='nasa'),
    path('tech_event', views.tech_events_data, name='tech_event'),
    path('nhl', views.nhl_data, name='nhl'),
    path('basketball', views.nba_data, name='basketball'),
    path('baseball', views.mlb_data, name='baseball'),
    path('top_podcasts', views.itunes_podcasts_data, name='top_podcasts'),
]