from django.contrib.auth import get_user_model
from django.db import models

CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
)

User = get_user_model()


class Achievement(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16, choices=CHOICES)
    birth_year = models.IntegerField()
    owner = models.ForeignKey(
        User, related_name='cats', on_delete=models.CASCADE)
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')

    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'
    
class Vaccine(models.Model):
    name = models.CharField(max_length=200)  # название вакцины

class CatVaccination(models.Model):
    cat = models.ForeignKey('Cat', on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    date = models.DateField()
    next_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.cat} - {self.vaccine} ({self.date})'

    @property
    def status(self):
        from datetime import date
        if self.completed:
            return 'completed'
        if self.next_date < date.today():
            return 'expired'
        return 'pending'


class Reminder(models.Model):
    cat = models.ForeignKey('Cat', on_delete=models.CASCADE, related_name='reminders')
    vaccination = models.ForeignKey(
        'CatVaccination', on_delete=models.CASCADE, related_name='reminders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(max_length=500)

    def __str__(self):
        return f'Reminder for {self.cat}: {self.message}'
