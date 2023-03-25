from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginSystem, name="login"),
    path("logout/", views.logoutSystem, name="logout"),
    path("register/", views.registerUser, name="register"),
    path("update-user/", views.updateUser, name="update-user"),
    
    path("", views.home, name="home"),
    path("topics/", views.topicsPage, name="topics"),
    path("activity/", views.activitiesPage, name="activity"),
    
    

    # pk = primary key
    path("profile/<str:pk>/", views.userProfile, name="user-profile"),

    path("room/<str:pk>/", views.room, name="room"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
]
