from django.db import models


class UserQuery(models.Model):
    """
    Сохраняет каждый запрос пользователя из Telegram-бота.
    Поля:
    - user_id     — Telegram ID пользователя
    - username    — Telegram username или имя
    - command     — введённая команда / текст
    - response    — ответ бота
    - created_at  — время запроса
    - is_resolved — пометка «разобрано» (для поддержки)
    - support_note — заметка администратора
    """

    user_id = models.BigIntegerField(verbose_name="Telegram ID")
    username = models.CharField(max_length=150, verbose_name="Пользователь")
    command = models.TextField(verbose_name="Команда / запрос")
    response = models.TextField(verbose_name="Ответ бота", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время")
    is_resolved = models.BooleanField(default=False, verbose_name="Разобрано")
    support_note = models.TextField(
        blank=True,
        verbose_name="Заметка администратора",
        help_text="Можно написать ответ на сложный вопрос пользователя здесь",
    )

    class Meta:
        verbose_name = "Запрос пользователя"
        verbose_name_plural = "Запросы пользователей"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.created_at:%d.%m.%Y %H:%M}] {self.username}: {self.command[:50]}"
