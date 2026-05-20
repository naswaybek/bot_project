from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserQuery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.BigIntegerField(verbose_name="Telegram ID")),
                (
                    "username",
                    models.CharField(max_length=150, verbose_name="Пользователь"),
                ),
                ("command", models.TextField(verbose_name="Команда / запрос")),
                (
                    "response",
                    models.TextField(blank=True, verbose_name="Ответ бота"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Время"
                    ),
                ),
                (
                    "is_resolved",
                    models.BooleanField(default=False, verbose_name="Разобрано"),
                ),
                (
                    "support_note",
                    models.TextField(
                        blank=True,
                        help_text="Можно написать ответ на сложный вопрос пользователя здесь",
                        verbose_name="Заметка администратора",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запрос пользователя",
                "verbose_name_plural": "Запросы пользователей",
                "ordering": ["-created_at"],
            },
        ),
    ]
