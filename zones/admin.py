from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Zone, ZoneCheckIn


@admin.register(Zone)
class ZoneAdmin(OSMGeoAdmin):
    list_display = ('id', 'owner', 'is_claimed', 'claimed_at', 'expires_at', 'xp_value')
    list_filter = ('claimed_at', 'expires_at', 'xp_value')
    search_fields = ('id', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-claimed_at',)

    def is_claimed(self, obj):
        return obj.is_claimed
    is_claimed.boolean = True


@admin.register(ZoneCheckIn)
class ZoneCheckInAdmin(OSMGeoAdmin):
    list_display = ('user', 'zone', 'timestamp', 'success')
    list_filter = ('timestamp', 'success')
    search_fields = ('user__username', 'zone__id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
