from .models import Link, Tag


def custom(request):
    return {'links': Link.objects.all(),
            'tags': Tag.objects.all()}