from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Category
from ..serializers import *
from django.shortcuts import get_object_or_404

class CategoryCreateAPIView(APIView):
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategoryUpdateAPIView(APIView):
    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDeleteAPIView(APIView):
    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(
            {"msg": "Category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class ItemCreateAPIView(APIView):
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemListAPIView(APIView):
    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class ItemUpdateAPIView(APIView):
    def put(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Item updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
class ItemDeleteAPIView(APIView):
    def delete(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return Response({
            "message": "Item deleted successfully",
            "id": pk
        }, status=status.HTTP_200_OK)

class ItemDetailAPIView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)




# 🔹 Create User
class EmployeeCreateAPIView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
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
class WareHouseLocationListAPIView(APIView):
    def get(self, request):
        warehouses = WareHouseLocation.objects.all()
        serializer = WareHouseLocationSerializer(warehouses, many=True)
        return Response(serializer.data)


# 🔹 Create View
class WareHouseLocationCreateAPIView(APIView):
    def post(self, request):
        serializer = WareHouseLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Retrieve View
class WareHouseLocationRetrieveAPIView(APIView):
    def get(self, request, pk):
        warehouse = get_object_or_404(WareHouseLocation, pk=pk)
        serializer = WareHouseLocationSerializer(warehouse)
        return Response(serializer.data)


# 🔹 Update View (PUT or PATCH)
class WareHouseLocationUpdateAPIView(APIView):
    def put(self, request, pk):
        warehouse = get_object_or_404(WareHouseLocation, pk=pk)
        serializer = WareHouseLocationSerializer(warehouse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# 🔹 Delete View
class WareHouseLocationDeleteAPIView(APIView):
    def delete(self, request, pk):
        warehouse = get_object_or_404(WareHouseLocation, pk=pk)
        warehouse.delete()
        return Response({"msg":"warehouse deleted successfully"},status=status.HTTP_204_NO_CONTENT)



# Create Block
class BlockCreateView(APIView):
    def post(self, request):
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List All Blocks
class BlockListView(APIView):
    def get(self, request):
        blocks = Block.objects.all()
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)

# Update Block
class BlockUpdateView(APIView):
    def put(self, request, pk):
        block = get_object_or_404(Block, pk=pk)
        serializer = BlockSerializer(block, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Block
class BlockDeleteView(APIView):
    def delete(self, request, pk):
        block = get_object_or_404(Block, pk=pk)
        block.delete()
        return Response({"msg": "Block deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
