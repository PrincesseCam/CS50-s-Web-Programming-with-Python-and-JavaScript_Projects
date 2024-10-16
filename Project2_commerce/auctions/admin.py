from django.contrib import admin
from .models import User, Categories, Listing, Bid, Comment

# Register your models here.

# #@admin.register(User)
#class UserAdmin(admin.ModelAdmin):#
#    list_display = ('username', 'email', 'is_staff', 'is_active')
#    search_fields = ('username', 'email')
#    list_filter = ('is_staff', 'is_active')

# #@admin.register(Categories)
#class CategoryAdmin(admin.ModelAdmin):#
#    list_display = ('categoryName',)
#    search_fields = ('categoryName',)

# #@admin.register(Listing)
#class AuctionListingAdmin(admin.ModelAdmin):
#    list_display = ('title', 'price', 'category', 'owner', 'isActive')
#    search_fields = ('title', 'description')
#    list_filter = ('isActive', 'category')
#    readonly_fields = ('created_at',)
#    fieldsets = (
#        (None, {
#            'fields': ('title', 'description', 'price', 'imageUrl', 'category', 'owner', 'isActive')
#        }),
#        ('Important dates', {
#            'fields': ('created_at',)
#        }),
#    )

# #@admin.register(Price)
#class BidAdmin(admin.ModelAdmin):
#    list_display = ('amount', 'user', 'listing')
#    search_fields = ('user__username', 'listing__title')
#    list_filter = ('listing',)

# #@admin.register(Comment)
#class CommentAdmin(admin.ModelAdmin):
#    list_display = ('user', 'listing', 'comment', 'created_at')
#    search_fields = ('user__username', 'listing__title', 'comment')
#    list_filter = ('listing', 'user')
#    readonly_fields = ('created_at',)
#    fieldsets = (
#        (None, {
#            'fields': ('user', 'listing', 'comment')
#        }),
#        ('Important dates', {
#            'fields': ('created_at',)
#        }),
#    )

# Register the models with the admin site
admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)