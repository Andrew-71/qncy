from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from vkhw.settings import CENTRIFUGO_URL, CENTRIFUGO_API_KEY

from cent import Client


def publish_server(channel):
    client = Client(CENTRIFUGO_URL, api_key=CENTRIFUGO_API_KEY)
    client.publish(channel, dict())


@csrf_exempt
def connect(request):
    response = {"result": {"user": "tutorial-user"}}
    return JsonResponse(response)


@csrf_exempt
def publish(request):
    response = {"result": {}}
    return JsonResponse(response)


@csrf_exempt
def subscribe(request):
    response = {"result": {}}
    return JsonResponse(response)
