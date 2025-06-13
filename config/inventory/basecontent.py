from django.db import models

class BaseContent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # set only once at creation
    updated_at = models.DateTimeField(auto_now=True)      # updates on every save

    class Meta:
        abstract = True 