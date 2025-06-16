from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from ..utils import success, error
from ..models import CustomUser
from ..serializers import SignupSerializer,UserSerializer
class EmployeeSignupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != CustomUser.UserType.ADMIN:
            return error("Only admins can create employees", status_code=403)

        data = request.data.copy()
        data['user_type'] = CustomUser.UserType.EMPLOYEE

        if CustomUser.objects.filter(email=data.get("email")).exists():
            return error("A user with this email already exists")

        serializer = SignupSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            data = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "user_type": user.user_type,
                }
            }

            return success("Employee created successfully", data, status_code=201)

        return error("Signup failed", serializer.errors)

class EmployeeListAPIView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                user = CustomUser.objects.get(id=id, user_type=CustomUser.UserType.EMPLOYEE)
                serializer = UserSerializer(user)
                return success("Employee fetched successfully", serializer.data)
            except CustomUser.DoesNotExist:
                return error("Employee not found", status_code=404)
        else:
            employees = CustomUser.objects.filter(user_type=CustomUser.UserType.EMPLOYEE)
            serializer = UserSerializer(employees, many=True)
            return success("Employees fetched successfully", serializer.data)
