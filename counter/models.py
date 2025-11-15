from django.db import models, transaction
from django.db.models import F

class ClickCounter(models.Model):
    count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Counter: {self.count}"
    
    @classmethod
    def get_current_count(cls):
        counter, created = cls.objects.get_or_create(pk=1)
        return counter.count
    
    @classmethod
    @transaction.atomic
    def increment(cls):
        counter, created = cls.objects.select_for_update().get_or_create(pk=1)
        counter.count = F('count') + 1
        counter.save(update_fields=['count'])
        counter.refresh_from_db()
        return counter.count
