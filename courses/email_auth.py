from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import serializers

User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    @property
    def fields(self):
        fields = super().fields
        # On retire username si présent, on ne garde que email et password
        fields.pop('username', None)
        fields['email'] = serializers.EmailField()
        fields['password'] = serializers.CharField()
        return fields

    def validate(self, attrs):
        email = attrs.get('email') or self.initial_data.get('email')
        password = attrs.get('password') or self.initial_data.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('Aucun utilisateur avec cet email.')
            credentials = {
                'username': user.username,
                'password': password
            }
            user = authenticate(**credentials)
            if user is None:
                raise serializers.ValidationError('Email ou mot de passe incorrect.')
            if not user.is_active:
                raise serializers.ValidationError('Ce compte est inactif.')
            # On passe username et password au parent
            data = super().validate({'username': user.username, 'password': password})
            return data
        else:
            raise serializers.ValidationError('Email et mot de passe requis.')

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
