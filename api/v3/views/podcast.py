from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from api.v1.serializers.medical import medicalCategoriesSerializer, medicalArtistsSerializer, medicalAlbumSerializer, \
    medicalTrackSerializer, medicalEpisodeSerializer
from apps.medical.models.models import medicalCategories, Artists, Album, Track


def AdminmedicalAllCategories(request):
    category = medicalCategories.objects.all()
    serializer = medicalCategoriesSerializer(category, many=True)
    return JsonResponse(serializer.data, safe=False)
@csrf_exempt
def AdminmedicalCategories(request, category_id):

    print('category_id', category_id)
    category_item = None
    category_items = medicalCategories.objects.filter(id=category_id)
    for category in category_items:
        category_item = medicalCategories.objects.filter(parent=category.id)
        print('category_item', category_item)
    serializer = medicalCategoriesSerializer(category_item, many=True)
    return JsonResponse(serializer.data, safe=False)

def AdminmedicalAllArtists(request ):
    artists_item = Artists.objects.all()
    serializer = medicalArtistsSerializer(artists_item, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def AdminmedicalArtists(request, artists_id):
    artists_item = None
    artists = Artists.objects.filter(id=artists_id)
    for artist in artists:
        artists_item = Artists.objects.filter(id=artist.id)

    serializer = medicalArtistsSerializer(artists_item, many=True)
    return JsonResponse(serializer.data, safe=False)




def AdminmedicalAllAlbum(request ):
    album_item = Album.objects.all()
    serializer = medicalAlbumSerializer(album_item, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def AdminmedicalAlbum(request, album_id):
    album_item = None
    albums = Album.objects.filter(id=album_id)
    for album in albums:
        album_item = Album.objects.filter(id=album.id)

    serializer = medicalAlbumSerializer(album_item, many=True)
    return JsonResponse(serializer.data, safe=False)


def AdminmedicalAllTrack(request ):
    track_item = Track.objects.all()
    serializer = medicalTrackSerializer(track_item, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def AdminmedicalTrack(request, track_id):
    track_item = None
    tracks = Track.objects.filter(id=track_id)
    for track in tracks:
        track_item = Track.objects.filter(id=track.id)

    serializer = medicalTrackSerializer(track_item, many=True)
    return JsonResponse(serializer.data, safe=False)


def AdminmedicalAllEpisode(request ):
    episode_item = Track.objects.all()
    serializer = medicalEpisodeSerializer(episode_item, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def AdminmedicalEpisode(request, episode_id):
    episode_item = None
    episodes = Track.objects.filter(id=episode_id)
    for episode in episodes:
        episode_item = Track.objects.filter(id=episode.id)

    serializer = medicalEpisodeSerializer(episode_item, many=True)
    return JsonResponse(serializer.data, safe=False)


def AdminmedicalAllEvents(request ):
    event_item = Track.objects.all()
    serializer = medicalEpisodeSerializer(event_item, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def AdminmedicalEvents(request, event_id):
    event_item = None
    events = Track.objects.filter(id=event_id)
    for event in events:
        event_item = Track.objects.filter(id=event.id)

    serializer = medicalEpisodeSerializer(event_item, many=True)
    return JsonResponse(serializer.data, safe=False)
