# accounts/pipeline.py
from django.shortcuts import redirect
from .models import User

def create_user_from_google(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}
    
    email = details.get('email')
    if not email:
        return redirect('login_error')
    
    # Check if user already exists
    try:
        user = User.objects.get(email=email)
        return {
            'is_new': False,
            'user': user
        }
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create(
            email=email,
            username=email,  # Use email as username
            first_name=details.get('first_name', ''),
            last_name=details.get('last_name', ''),
            is_verified=True,  # Google emails are verified
            google_id=kwargs.get('response', {}).get('sub', ''),
            user_type='customer'
        )
        user.set_unusable_password()  # Google users don't need password
        user.save()
        
        return {
            'is_new': True,
            'user': user
        }