from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "division", "category", "created_at", "is_processed")
    list_filter = ("division", "category", "is_processed", "created_at")
    search_fields = ("name", "email", "organisation", "division", "category", "message")
    readonly_fields = ("created_at",)
    list_editable = ("is_processed",)
