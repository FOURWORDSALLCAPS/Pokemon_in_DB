import folium

from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import Pokemon
from django.utils.timezone import localtime


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemons = Pokemon.objects.all()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon in pokemons:
        for pokemon_entity in pokemon.pokemonentity_set.all():
            if pokemon.image and pokemon_entity.disappeared_at > localtime() > pokemon_entity.appeared_at:
                add_pokemon(
                    folium_map, pokemon_entity.lat,
                    pokemon_entity.lon,
                    request.build_absolute_uri(pokemon.image.url)
                )

    pokemons_on_page = []
    for pokemon in pokemons:
        pokemon_entities = pokemon.pokemonentity_set.filter(disappeared_at__gt=localtime(), appeared_at__lt=localtime())
        if pokemon_entities.exists():
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else None,
                'title_ru': pokemon.title,
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        requested_pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon.pokemonentity_set.all():
        if requested_pokemon.image and pokemon_entity.disappeared_at > localtime() > pokemon_entity.appeared_at:
            add_pokemon(
                folium_map, pokemon_entity.lat,
                pokemon_entity.lon,
                request.build_absolute_uri(requested_pokemon.image.url)
            )

    pokemons_on_page = []
    pokemon_entities = requested_pokemon.pokemonentity_set.filter(disappeared_at__gt=localtime(),
                                                                  appeared_at__lt=localtime())
    if pokemon_entities.exists():
        pokemons_on_page.append({
            'pokemon_id': requested_pokemon.id,
            'img_url': request.build_absolute_uri(requested_pokemon.image.url) if requested_pokemon.image else None,
            'title_ru': requested_pokemon.title,
        })

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemons_on_page[0]
    })
