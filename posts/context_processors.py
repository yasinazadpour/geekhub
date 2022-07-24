from .models import HotLink, Link, Tag


def custom(request):
    tags = sorted(
        list(Tag.objects.all()), 
        key=lambda tag: tag.taged_posts.count(), 
        reverse=True
        )
    return {'links': Link.objects.all(),
            'tags': tags,
            'hotlinks': HotLink.objects.all()}