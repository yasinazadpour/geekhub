from .models import HotLink, Link, Tag


def custom(request):
    return {'links': Link.objects.all(),
            'tags': Tag.objects.all(),
            'hotlinks': HotLink.objects.all()}