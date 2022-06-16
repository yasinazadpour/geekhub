from .models import Link


def custom(request):
    return {'links': Link.objects.all()}