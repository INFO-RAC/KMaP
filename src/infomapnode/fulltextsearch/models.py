from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.dispatch import receiver
from django.db.models import signals

from geonode.layers.models import ResourceBase


class FullText(models.Model):
    base = models.OneToOneField(ResourceBase, on_delete=models.CASCADE)
    content = models.TextField(default=None, null=True)
    svf = SearchVectorField(default=None, null=True)

    def __str__(self):
        return f"{self.base.title}[{len(self.svf or '')}]"

    class Meta:
        indexes = (GinIndex(fields=["svf"]),)


@receiver(signals.post_save, sender=FullText)
def post_save_service(instance, sender, created, **kwargs):
    FullText.objects.filter(id=instance.id).update(svf=SearchVector('content'))
