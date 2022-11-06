from django.db import models


class PickPeriod(models.Model):
    days = models.IntegerField(blank=False, null=False)
    all_time = models.BooleanField(blank=False, null=False, default=False)

    def __str__(self):
        return str(self.days) + ' Days' if self.days else 'All Time'


class MostPickedCardPickRate(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    percentage = models.IntegerField(null=False, blank=False)
    period = models.ForeignKey(PickPeriod, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.card.name} {self.percentage}% ({str(self.period.days) + " Days" if self.period.days else "All Time"})'


class AttributePickRate(models.Model):
    card_attr = models.ForeignKey('CardColour', on_delete=models.CASCADE)
    percentage = models.IntegerField(null=False, blank=False)
    period = models.ForeignKey(PickPeriod, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.card_attr.name} {self.percentage}% ({str(self.period.days) + " Days" if self.period.days else "All Time"})'


class CardTypePickRate(models.Model):
    card_type = models.ForeignKey('Type', on_delete=models.CASCADE)
    period = models.ForeignKey(PickPeriod, on_delete=models.CASCADE)
    percentage = models.IntegerField(null=False, blank=False)


class CardTotalCostPickRate(models.Model):
    period = models.ForeignKey(PickPeriod, on_delete=models.CASCADE)
    percentage = models.IntegerField(null=False, blank=False)
    total_cost = models.IntegerField(null=False, blank=False)