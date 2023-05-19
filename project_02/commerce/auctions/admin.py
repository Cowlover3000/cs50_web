from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Listing, Category, Comment, Bid, User, Watchlist

admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(User, UserAdmin)
admin.site.register(Watchlist)