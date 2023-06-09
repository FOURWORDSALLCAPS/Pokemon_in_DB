import folium

from django.shortcuts import render
from .models import Pokemon, PokemonEntity
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404

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
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    current_time = localtime()
    pokemon_entities = PokemonEntity.objects.select_related('pokemon').filter(disappeared_at__gt=current_time,
                                                                              appeared_at__lt=current_time)
    for entity in pokemon_entities:
        if entity.pokemon.image:
            add_pokemon(
                folium_map, entity.lat,
                entity.lon,
                request.build_absolute_uri(entity.pokemon.image.url)
            )

    pokemons_on_page = []
    for entity in pokemon_entities:
        if entity.pokemon.image:
            pokemons_on_page.append({
                'pokemon_id': entity.pokemon.id,
                'img_url': request.build_absolute_uri(entity.pokemon.image.url),
                'title_ru': entity.pokemon.title,
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    requested_pokemon = get_object_or_404(Pokemon, id=pokemon_id)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    current_time = localtime()
    pokemon_entity = PokemonEntity.objects.select_related('pokemon').filter(disappeared_at__gt=current_time,
                                                                            appeared_at__lt=current_time).first()
    if requested_pokemon.image:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(requested_pokemon.image.url)
        )

    pokemons_on_page = []
    pokemon_entities = requested_pokemon.entities.filter(disappeared_at__gt=current_time,
                                                         appeared_at__lt=current_time)
    evolution = {
        'previous_evolution': None,
        'next_evolution': None
    }

    if requested_pokemon.previous_evolution is not None:
        previous_evolution = requested_pokemon.previous_evolution
        evolution['previous_evolution'] = {
            'pokemon_id': previous_evolution.id,
            'img_url': request.build_absolute_uri(
                previous_evolution.image.url) if previous_evolution.image else None,
            'title_ru': previous_evolution.title
        }

    if requested_pokemon.next_evolutions is not None and requested_pokemon.next_evolutions.filter(
            id__isnull=False).exists():
        next_evolution = requested_pokemon.next_evolutions.filter(id__isnull=False).first()
        evolution['next_evolution'] = {
            'pokemon_id': next_evolution.id,
            'img_url': request.build_absolute_uri(
                next_evolution.image.url) if next_evolution.image else None,
            'title_ru': next_evolution.title
        }

    if pokemon_entities.exists():
        pokemons_on_page.append({
            'pokemon_id': requested_pokemon.id,
            'img_url': request.build_absolute_uri(requested_pokemon.image.url) if requested_pokemon.image else None,
            'title_ru': requested_pokemon.title,
            'description': requested_pokemon.description,
            'title_en': requested_pokemon.title_en,
            'title_jp': requested_pokemon.title_jp,
            'previous_evolution': evolution['previous_evolution'],
            'next_evolution': evolution['next_evolution'],
        })

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemons_on_page[0]
    })
