## 0.5.0 (2024-11-18)

### Feat

- add users/me API
- add CORS_ALLOWED_ORIGINS to settings

## 0.4.0 (2024-11-14)

### Feat

- add TokenVerifyView
- add TokenBlacklistView
- add TokenRefreshView
- add TokenObtainPairView
- add UserActivateView
- use UUID in activation link instead of id
- add uuid field to User model
- add debug-toolbar in local environment
- disable logs on admin page
- send activation email to user on registration
- add get_activation_link method to User model
- add AccountActivationTokenGenerator
- add UserRegistrationViewSet
- add UserRegistrationSerializer
- add mailpit to local env setup

### Fix

- FRONTEND_URL only present in local.py
- URLs does not end with /
- UserSerializer saving password incorrectly
- rest_framework missing from INSTALLED_APPS

## 0.3.0 (2024-11-13)

### Feat

- add users app with initial User model

### Fix

- username field not used in create user methods

## 0.2.0 (2024-11-09)

### Feat

- create initial django project
