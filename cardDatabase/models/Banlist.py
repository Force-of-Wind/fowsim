from django.db import models


class Format(models.Model):
    name = models.TextField(blank=False, null=False, default='')

    def __str__(self):
        return self.name
    
    @classmethod
    def get_default(cls):
        format, created = cls.objects.get_or_create(
            name='Wanderer',
        )
        return format.pk


# Universally banned cards by themselves
class BannedCard(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    format = models.ForeignKey('Format', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.card.name} ({self.format.name})'


class CombinationBannedCards(models.Model):
    format = models.ForeignKey('Format', on_delete=models.CASCADE)
    cards = models.ManyToManyField('Card', related_name='cards')

    def __str__(self):
        return f'{str(list(self.cards.all().values_list("name", flat=True)))} ({self.format.name})'