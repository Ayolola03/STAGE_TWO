from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserSerializer, OrganisationSerializer
from .models import User, Organisation
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Create an organization for the user
            org_name = f"{user.first_name}'s Organisation"
            organisation = Organisation.objects.create(
                name=org_name,
                description="Default organisation",
            )
            organisation.users.add(user)

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "accessToken": str(refresh.access_token),
                        "refreshToken": str(refresh),
                        "user": UserSerializer(user).data,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "Bad Request",
                "message": "Registration unsuccessful",
                "statusCode": 422,
                "errors": serializer.errors,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": str(access_token),
                        "refreshToken": str(refresh),
                        "user": UserSerializer(user).data,
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            return Response(
                {
                    "status": "success",
                    "message": "User retrieved successfully",
                    "data": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User not found",
                    "statusCode": 404,
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class OrganisationListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organisations = Organisation.objects.filter(users=request.user)
        return Response(
            {
                "status": "success",
                "message": "Organisations retrieved successfully",
                "data": OrganisationSerializer(organisations, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
