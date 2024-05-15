from django.db import models
from django.utils import timezone


class Answer(models.Model):
    """An answer to a feedback question."""

    # The id of the session, if provided.
    # We use the session id as a primary key and not the Django-internal
    # primary key to avoid that duplicate answers are loaded from fixtures.
    session_id = models.CharField(max_length=255, default='unknown', primary_key=True)

    # The id of the user.
    user_id = models.TextField(max_length=100)

    # The text of the question. Max length: 300 symbols.
    question_text = models.TextField(max_length=300)

    # The base 64 encoded image of this question, if provided.
    # Max size: 10MB (10M symbols in base 64).
    question_image = models.TextField(null=True, blank=True, max_length=10_000_000)

    # The value of the answer, if provided. Max length: 1000 symbols.
    # This can be:
    # - a likert value ("strongly agree", ...), 
    # - a binary value ("yes", ...),
    # - or another form of text such as a user input.
    value = models.TextField(null=True, blank=True, max_length=1_000)

    # The date of this answer. Added by the service and not configurable by the user.
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.question_text}: {self.value} (ID {self.user_id})"

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ["-date"]
