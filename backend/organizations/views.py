from rest_framework import status, views, permissions
from rest_framework.response import Response
from .models import Organization
from .serializers import OrganizationSerializer, OrganizationMemberSerializer
from .permissions import IsOrganizationMember, IsOrganizationAdmin
from accounts.models import User

class CurrentOrganizationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({"error": "No organization associated with this account."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrganizationSerializer(org).data)

    def patch(self, request):
        org = request.user.organization
        if not org:
            return Response({"error": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role not in ("owner", "admin"):
            return Response({"error": "Only owners or admins can modify organization details."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrganizationMembersView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org:
            return Response([], status=status.HTTP_200_OK)
        members = org.users.all().order_by("created_at")
        return Response(OrganizationMemberSerializer(members, many=True).data)

    def post(self, request):
        org = request.user.organization
        if not org:
            return Response({"error": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role not in ("owner", "admin"):
            return Response({"error": "Only owners or admins can add members."}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get("email", "").strip().lower()
        name = request.data.get("name", "").strip()
        role = request.data.get("role", "member")
        password = request.data.get("password", "Welcome2026!")

        if not email or not name:
            return Response({"error": "Name and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        member = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            organization=org,
            role=role if role in ("admin", "member") else "member"
        )
        return Response(OrganizationMemberSerializer(member).data, status=status.HTTP_201_CREATED)
