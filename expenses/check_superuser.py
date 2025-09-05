from django.http import JsonResponse
from django.contrib.auth import get_user_model

def check_superuser(request):
    User = get_user_model()
    superusers = User.objects.filter(is_superuser=True)
    data = {
        "count": superusers.count(),
        "superusers": [u.username for u in superusers],
    }
    return JsonResponse(data)
