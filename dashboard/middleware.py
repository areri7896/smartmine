from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                if not request.user.profile.is_complete:
                    profile_url = reverse('profile')
                    logout_url = reverse('account_logout') 
                    # Allow access to profile page, logout, and static/media files
                    if request.path != profile_url and request.path != logout_url and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                        return redirect('profile')
            except Exception:
                # Handle cases where user might not have a profile yet (though signals should prevent this)
                pass

        response = self.get_response(request)
        return response
