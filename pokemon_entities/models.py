from django.db import models
from django.utils import timezone


class Pokemon(models.Model):
    title = models.CharField('Имя', max_length=200)
    image = models.ImageField('Картинка', upload_to='pokemons', blank=True)
    description = models.TextField('Описание', blank=True, null=True)
    title_en = models.CharField('Имя на en', max_length=200, blank=True)
    title_jp = models.CharField('Имя на jp', max_length=200, blank=True)
    previous_evolution = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                           verbose_name='Предыдущая эволюция', related_name='next_evolutions')

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, verbose_name='Покемон', related_name='entities')
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    appeared_at = models.DateTimeField('Появился')
    disappeared_at = models.DateTimeField('Исчез')
    level = models.IntegerField('Уровень', null=True, blank=True)
    health = models.IntegerField('Здоровье', null=True, blank=True)
    strength = models.IntegerField('Сила', null=True, blank=True)
    defence = models.IntegerField('Защита', null=True, blank=True)
    stamina = models.IntegerField('Выносливость', null=True, blank=True)

    def __str__(self):
        return str(self.pokemon)
