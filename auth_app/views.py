from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserSerializer, OrganisationSerializer
from .models import User, Organisation
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Handles user registration
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Ensure user is saved before creating token.
            user.save()

            # Create an organization for the user.
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

# Handles login
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # The Response when login credentials are correct.
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
        # The Response when there's an issue logging in.
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


class OrganisationDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        try:
            organisation = Organisation.objects.get(org_id=org_id)
            if organisation.users.filter(id=request.user.id).exists():
                return Response(
                    {
                        "status": "success",
                        "message": "Organisation retrieved successfully",
                        "data": OrganisationSerializer(organisation).data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "status": "Forbidden",
                    "message": "You do not have permission to view this organisation",
                    "statusCode": 403,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except Organisation.DoesNotExist:
            return Response(
                {
                    "status": "Not Found",
                    "message": "Organisation not found",
                    "statusCode": 404,
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class OrganisationCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)
            return Response(
                {
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": OrganisationSerializer(organisation).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class AddUserToOrganisationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        user_id = request.data.get("userId")
        try:
            user = User.objects.get(user_id=user_id)
            organisation = Organisation.objects.get(org_id=org_id)
            if request.user in organisation.users.all():
                organisation.users.add(user)
                return Response(
                    {
                        "status": "success",
                        "message": "User added to organisation successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "status": "Forbidden",
                    "message": "You do not have permission to modify this organisation",
                    "statusCode": 403,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except (User.DoesNotExist, Organisation.DoesNotExist):
            return Response(
                {
                    "status": "Not Found",
                    "message": "User or Organisation not found",
                    "statusCode": 404,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
