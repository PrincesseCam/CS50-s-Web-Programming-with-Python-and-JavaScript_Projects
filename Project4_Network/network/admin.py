from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Post, User, Comment, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_followers_count', 'get_following_count')
    
    # Add followers to fieldsets while keeping original UserAdmin fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Network Connections', {
            'fields': ('followers',),
            'description': 'Manage user followers'
        }),
    )
    
    # Add followers to filter_horizontal for better UI
    filter_horizontal = ('followers', 'groups', 'user_permissions')
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    get_followers_count.short_description = 'Followers'
    
    def get_following_count(self, obj):
        return obj.following.count()
    get_following_count.short_description = 'Following'

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(Post)
admin.site.register(Comment)