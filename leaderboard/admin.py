from django.contrib import admin
from .models import LeaderboardEntry, LeaderboardSnapshot


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'rank', 'score', 'last_updated')
    list_filter = ('category', 'last_updated')
    search_fields = ('user__username',)
    ordering = ('category', 'rank')
    readonly_fields = ('last_updated',)


@admin.register(LeaderboardSnapshot)
class LeaderboardSnapshotAdmin(admin.ModelAdmin):
    list_display = ('category', 'snapshot_date')
    list_filter = ('category', 'snapshot_date')
    ordering = ('-snapshot_date',)
    readonly_fields = ('snapshot_date', 'data')
