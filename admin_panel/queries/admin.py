from django.contrib import admin
from django.utils.html import format_html
from .models import UserQuery


@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    """
    Настройка отображения запросов в Django-админке.
    Позволяет:
    - просматривать историю всех запросов
    - фильтровать по пользователю, дате, статусу
    - искать по команде и имени пользователя
    - добавлять заметки поддержки и помечать как разобранные
    """

    # Колонки в списке
    list_display = (
        "created_at",
        "username",
        "user_id",
        "short_command",
        "short_response",
        "is_resolved",
        "has_note",
    )

    # Фильтры в правой панели
    list_filter = ("is_resolved", "created_at")

    # Поиск
    search_fields = ("username", "command", "response", "user_id")

    # Сортировка по умолчанию
    ordering = ("-created_at",)

    # Поля, редактируемые прямо в списке
    list_editable = ("is_resolved",)

    # Количество записей на странице
    list_per_page = 30

    # Поля в форме редактирования
    fieldsets = (
        (
            "Информация о пользователе",
            {
                "fields": ("user_id", "username", "created_at"),
            },
        ),
        (
            "Запрос и ответ",
            {
                "fields": ("command", "response"),
            },
        ),
        (
            "Поддержка",
            {
                "fields": ("is_resolved", "support_note"),
                "description": (
                    "Если пользователь задал сложный вопрос, "
                    "напишите ответ в поле «Заметка» и пометьте как разобранное."
                ),
            },
        ),
    )

    # Поля только для чтения в форме
    readonly_fields = ("user_id", "username", "command", "response", "created_at")

    # ──────────────────────────────────────────
    # Вычисляемые колонки
    # ──────────────────────────────────────────

    @admin.display(description="Команда")
    def short_command(self, obj):
        return obj.command[:60] + "…" if len(obj.command) > 60 else obj.command

    @admin.display(description="Ответ бота")
    def short_response(self, obj):
        return obj.response[:60] + "…" if len(obj.response) > 60 else obj.response

    @admin.display(description="Заметка", boolean=True)
    def has_note(self, obj):
        return bool(obj.support_note)

    # ──────────────────────────────────────────
    # Групповые действия
    # ──────────────────────────────────────────

    actions = ["mark_resolved", "mark_unresolved"]

    @admin.action(description="Пометить выбранные как разобранные")
    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f"Помечено разобранными: {updated} записей.")

    @admin.action(description="Снять отметку «разобрано»")
    def mark_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False)
        self.message_user(request, f"Отметка снята с {updated} записей.")


# Настройка заголовков сайта
admin.site.site_header = "🤖 Админка чат-бота"
admin.site.site_title = "Бот — управление"
admin.site.index_title = "Панель управления"
