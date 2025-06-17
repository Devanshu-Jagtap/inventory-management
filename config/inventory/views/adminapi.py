from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Category
from ..serializers import *
from django.shortcuts import get_object_or_404

class CategoryAPIView(APIView):
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user.effective_admin)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        categories = Category.objects.filter(owner=request.user.effective_admin)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk,owner=request.user.effective_admin)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk,owner=request.user.effective_admin)
        category.delete()
        return Response(
            {"msg": "Category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class ItemAPIView(APIView):
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user.effective_admin)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        items = Item.objects.filter(owner=request.user.effective_admin)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        item = get_object_or_404(Item, pk=pk,owner=request.user.effective_admin)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Item updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(Item, pk=pk,owner=request.user.effective_admin)
        item.delete()
        return Response({
            "message": "Item deleted successfully",
            "id": pk
        }, status=status.HTTP_200_OK)

class ItemDetailAPIView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk,owner=request.user.effective_admin)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)




# 🔹 Create User
# class EmployeeCreateAPIView(APIView):
#     def post(self, request):
#         data = request.data.copy()
#         data['admin_owner'] = request.user.effective_admin().id
#         serializer = CustomUserSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeCreateAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        data['admin_owner'] = request.user.effective_admin.id  # ✅ This is OK

        serializer = CustomUserSerializer(data=data, context={'request': request})  # ✅ Use `data`, not `request.data`
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔹 List Users
class EmployeeListAPIView(APIView):
    def get(self, request):
        users = CustomUser.objects.filter(user_type="employee")
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)


class EmployeeUpdateAPIView(APIView):
    def put(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDeleteAPIView(APIView):
    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response({
            "message": "User deleted successfully",
            "id": pk
        }, status=status.HTTP_200_OK)

class EmployeeDetailAPIView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 List View
class WareHouseLocationAPIView(APIView):
    def get(self, request):
        warehouses = WareHouseLocation.objects.filter(owner=request.user.effective_admin)
        serializer = WareHouseLocationSerializer(warehouses, many=True)
        return Response(serializer.data)


# 🔹 Create View
    def post(self, request):
        serializer = WareHouseLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user.effective_admin)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Retrieve View
    def get(self, request, pk):
        warehouse = get_object_or_404(WareHouseLocation, pk=pk,owner=request.user.effective_admin)
        serializer = WareHouseLocationSerializer(warehouse)
        return Response(serializer.data)


# 🔹 Update View (PUT or PATCH)
    def put(self, request, pk):
        warehouse = get_object_or_404(WareHouseLocation, pk=pk,owner=request.user.effective_admin)
        serializer = WareHouseLocationSerializer(warehouse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# 🔹 Delete View
    def delete(self, request, pk):
        warehouse = get_object_or_404(WareHouseLocation, pk=pk)
        warehouse.delete()
        return Response({"msg":"warehouse deleted successfully"},status=status.HTTP_204_NO_CONTENT)



# Create Block
class BlockAPIView(APIView):
    def post(self, request):
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List All Blocks
    def get(self, request):
        blocks = Block.objects.all()
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)

# Update Block
    def put(self, request, pk):
        block = get_object_or_404(Block, pk=pk)
        serializer = BlockSerializer(block, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Block
    def delete(self, request, pk):
        block = get_object_or_404(Block, pk=pk)
        block.delete()
        return Response({"msg": "Block deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
