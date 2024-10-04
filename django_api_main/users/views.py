from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from django.db import transaction, IntegrityError

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
  username = request.data.get('username')
  password = request.data.get('password')

  if not username or not password:
    return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

  try:
    # Use transaction to ensure rollback on failure
    with transaction.atomic():
      # Check if the username is already taken
      if User.objects.filter(username=username).exists():
        return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

      # Create the user
      user = User.objects.create_user(username=username, password=password)

      # Create the token
      token, _ = Token.objects.get_or_create(user=user)

      # Successful registration response
      return Response({"success": True, "token": token.key}, status=status.HTTP_201_CREATED)

  except IntegrityError as e:
        # Rollback the transaction in case of IntegrityError
        return Response({"error": "A database error occurred, please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  except Exception as e:
        # Catch-all for other unforeseen errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
  print("Login user...")
  username = request.data.get('username')
  password = request.data.get("password")
  user = authenticate(username=username, password=password)
  print(user)
  if user is not None:
    try:
      token, _ = Token.objects.get_or_create(user=user)
      return Response({"success": True, "token": token.key}, status=status.HTTP_200_OK)
    except IntegrityError as e:
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  else: 
    return Response({"success": False}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def get_users(request):
  try:
    users = User.objects.all().values()
    return Response(users, status=status.HTTP_200_OK)
  except IntegrityError as e:
      return Response({"error": f"Database Error, {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
