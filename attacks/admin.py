from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Attack, AttackCooldown


@admin.register(Attack)
class AttackAdmin(OSMGeoAdmin):
    list_display = ('attacker', 'defender', 'zone', 'result', 'success', 'xp_gained', 'timestamp')
    list_filter = ('result', 'success', 'timestamp')
    search_fields = ('attacker__username', 'defender__username', 'zone__id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(AttackCooldown)
class AttackCooldownAdmin(admin.ModelAdmin):
    list_display = ('user', 'zone', 'last_attack', 'cooldown_until', 'is_on_cooldown')
    list_filter = ('last_attack', 'cooldown_until')
    search_fields = ('user__username', 'zone__id')

    def is_on_cooldown(self, obj):
        return obj.is_on_cooldown
    is_on_cooldown.boolean = True
