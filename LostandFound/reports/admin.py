from django.contrib import admin
from .models import Lost,Found,MatchedItem


class Lostadmin(admin.ModelAdmin):
    list_display=['id','user','item_name','location','category','item_desc','date']
class Foundadmin(admin.ModelAdmin):
    list_display=['id','user','item_name','location','category','item_desc','image_url','date']
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id','lost_item_id', 'found_item_id','is_collected','date',"collected_by"]
    list_filter = ['is_collected']
    list_editable = ['is_collected'] 
    search_fields = ['lost_item__item_desc', 'found_item__item_desc']
admin.site.register(Lost, Lostadmin)
admin.site.register(Found, Foundadmin)
admin.site.register(MatchedItem, MatchAdmin)