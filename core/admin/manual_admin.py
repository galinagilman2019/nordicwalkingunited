from django.contrib import admin
from core.models.nwu_manual import NWU_Manual

@admin.register(NWU_Manual)
class NWUManualAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "order", "updated_at")
    list_filter = ("audience",)
    search_fields = ("title", "body")
    ordering = ("audience", "order")
    prepopulated_fields = {"slug": ("title",)}

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
