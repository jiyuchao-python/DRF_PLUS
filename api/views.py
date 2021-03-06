from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.models import Book
from utils.response import APIResponse
from .serializers import BookModelSerializer, BookDeModelSerializer, BookModelSerializerV2
from api.serializers import BookModelSerializer


class BookAPIView(APIView):

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("id")
        if book_id:

            book_obj = Book.objects.get(pk=book_id)
            book_data = BookModelSerializer(book_obj).data
            return Response({
                "status": status.HTTP_200_OK,
                "message": "查询单个图书成功",
                # "results":book_obj
                "results": book_data
            })

        else:
            book_list = Book.objects.filter(is_delete=False)
            book_list_data = BookModelSerializer(book_list, many=True).data
            return Response({
                "status": status.HTTP_200_OK,
                "message": "查询所有图书成功",
                # "results": book_list
                "results": book_list_data
            })

class BookAPIViewV2(APIView):
    def post(self, request, *args, **kwargs):
        request_data = request.data
        if isinstance(request_data, dict):
            many = False
        elif isinstance(request_data, list):
            many = True
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "请求参数格式有误",
            })
        book_data = BookDeModelSerializer(data=request_data,many=many)
        book_data.is_valid(raise_exception=True)
        book_obj = book_data.save()
        return APIResponse(results=book_obj)
        # return Response({
        #     "status": status.HTTP_200_OK,
        #     "msg": "添加图书成功",
        #     "result": BookModelSerializer(book_obj,many=many).data
        # })

    def delete(self, request, *args, **kwargs):
        book_id = kwargs.get("id")
        if book_id:
            ids = [book_id]
        else:
            ids = request.data.get("ids")
        response = Book.objects.filter(pk__in=ids, is_delete=False).update(is_delete=True)
        if response:
            return APIResponse(200,"删除成功")
            # return Response({
            #     "status": status.HTTP_200_OK,
            #     "msg": "删除成功"
            # })
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "msg": "删除失败或图书不存在"
        })

    def put(self, request, *args, **kwargs):
        request_data = request.data
        book_id = kwargs.get("id")
        try:
            book_obj = Book.objects.get(pk=book_id)
        except:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "图书不存在"
            })
        book_data = BookModelSerializerV2(data=request_data, instance=book_obj)
        book_data.is_valid(raise_exception=True)
        book_data.save()
        return APIResponse(400,"更新成功",results=book_data)
        # return Response({
        #     "status": status.HTTP_400_BAD_REQUEST,
        #     "message": "更新成功",
        #     "results": BookModelSerializerV2(book_obj).data
        # })


    # def patch(self, request, *args, **kwargs):
    #     request_data = request.data
    #     book_id = kwargs.get("id")
    #     try:
    #         book_obj = Book.objects.get(pk=book_id)
    #     except:
    #         return Response({
    #             "status": status.HTTP_400_BAD_REQUEST,
    #             "message": "图书不存在"
    #         })
    #     # book_ser = BookModelSerializerV2(data=request_data, instance=book_obj)
    #     book_ser = BookModelSerializerV2(data=request_data, instance=book_obj, partial=True)
    #     book_ser.is_valid(raise_exception=True)
    #     book_ser.save()
    #     return Response({
    #         "status": status.HTTP_400_BAD_REQUEST,
    #         "message": "更新成功",
    #         "results": BookModelSerializerV2(book_obj).data
    #     })
    def patch(self, request, *args, **kwargs):
        request_data = request.data
        book_id = kwargs.get("id")
        if book_id and isinstance(request_data, dict):
            book_ids = [book_id, ]
            request_data = [request_data]
        elif not book_id and isinstance(request_data, list):
            book_ids = []
            for dic in request_data:
                pk = dic.pop("pk", None)
                if pk:
                    book_ids.append(pk)
                else:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "PK不存在",
                    })
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "数据格式有误",
                })
            book_list = []
            new_data = []
            for index, pk in enumerate(book_ids):
                try:
                    book_obj = Book.objects.get(pk=pk)
                    book_list.append(book_obj)
                    new_data.append(request_data[index])
                except:
                    continue
            book_ser = BookModelSerializerV2(data=new_data, instance=book_list, partial=True, many=True)
            book_ser.is_valid(raise_exception=True)
            book_ser.save()

            # return Response({
            #     "status": status.HTTP_200_OK,
            #     "message": "修改成功",
            # })
            return APIResponse(100,"修改成功")
