from django.db.models import Prefetch, Count, Avg
from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url

        return rep

    def create(self, validated_data):
        data = validated_data.copy()

        user = User(**data)
        user.set_password(data["password"])
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }



class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['picture'] = instance.picture.url

        return rep

class ImageSerializer(ItemSerializer):
    picture = serializers.ImageField()
    # def to_representation(self, instance):
    #     return instance.picture.url

    def create(self, validated_data):
        data = validated_data.copy()

        picture = JourneyPictures(**data)
        picture.save()

        return picture

    class Meta:
        model = JourneyPictures
        fields = ["id","picture"]



class PostTinTucSerializer(serializers.ModelSerializer):  # 1 user n post
    pic = ImageSerializer(many=True, read_only=True)
    danhmuc = serializers.PrimaryKeyRelatedField(queryset=DanhMuc.objects.all())

    def create(self, validated_data):
        pictures_data = validated_data.pop('pic', [])
        danhMuc = validated_data.pop('danhmuc', None)
        print('dawda',validated_data)
        post = BaiDangTinTuc.objects.create(
            **validated_data,
            danhmuc=danhMuc

        )
        return post

    class Meta:
        model = BaiDangTinTuc
        fields = ["id", "created_date", "content", "title", 'pic','danhmuc']


class HanhKhanhSerializer(serializers.ModelSerializer):
    class Meta:
        model = NguoiThan
        fields = ['id', 'ten', 'namsinh']


class NguoiThanSerializer(ModelSerializer):
    class Meta:
        model = NguoiThan
        fields = ['id', 'ten', 'namsinh', 'created_date', 'updated_date']
        extra_kwargs = {'user': {'read_only': True}, 'active': {'read_only': True}}


class NguoiDangKySerializer(ModelSerializer):
    nguoi_than = NguoiThanSerializer(many=True, write_only=True)

    class Meta:
        model = NguoiDangKy
        fields = ['id', 'user', 'posts', 'timeselect', 'created_date', 'updated_date', 'nguoi_than']
        extra_kwargs = {'user': {'read_only': True}, 'active': {'read_only': True}}


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['id', 'content', 'created_date', 'user', 'reply_count']

    def get_reply_count(self, obj):
        return obj.comment_reply.count()

class TransportationsSerilializer (serializers.ModelSerializer):
    class Meta:
        model = Transportation
        fields = ['id','loai']


class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['id','diaChi']

class TagSerializer (serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']


class RouterSerializer(serializers.ModelSerializer):
    id_noiDi = LocalSerializer()
    id_noiDen = LocalSerializer()
    class Meta:
        model =Route
        fields = ['id_noiDi','id_noiDen']


class StopLocalSerializer(serializers.ModelSerializer):
    id_DiaDiem = LocalSerializer()
    class Meta:
        model = DiaDiemDungChan
        fields = ['ThoiGianDuKien', 'id_DiaDiem']

class JourneySerializer(serializers.ModelSerializer):
    # router
    id_tuyenDuong = RouterSerializer()
    id_PhuongTien = TransportationsSerilializer()
    stoplocal = serializers.SerializerMethodField(read_only=True)

    def get_stoplocal(self,obj):
        stop = DiaDiemDungChan.objects.filter(id_HanhTrinh = obj)
        return StopLocalSerializer(stop,many=True).data #json

    class Meta:
        model = Journey
        fields = ['ngayDi','ngayDen','id_tuyenDuong','id_PhuongTien','stoplocal']


class DanhMucSerializer(ModelSerializer):
    class Meta:
        model = DanhMuc
        fields = ['id', 'name', 'created_date', 'updated_date', 'active']

class PostSerializer(serializers.ModelSerializer): # 1 user n post
    journey = JourneySerializer(read_only=True)
    tags = TagSerializer(many=True,read_only=True)
    pic = ImageSerializer(many=True,read_only=True)
    gia = serializers.SerializerMethodField()
    soluongDaDat = serializers.SerializerMethodField(read_only=True)
    avgRate = serializers.SerializerMethodField(read_only=True)

    def get_avgRate(self, obj):
        print('daw',obj)
        avgRate = Rating.objects.filter(posts=obj).aggregate(Avg('rate'))
        # avgRate = int(avgRate['rate__avg'])
        print('dawdawda',avgRate)
        if avgRate.get('rate__avg') is not None:
            return avgRate['rate__avg']
        else:
            return 0


    def get_gia(self, obj):
        gia = GiaVe.objects.filter(tour=obj).values_list('gia',
                                                         flat=True)  # Thay thế 'field1' bằng trường bạn muốn lấy
        return list(gia)


    def get_soluongDaDat(self, obj):
        soluong = obj.nguoidangky_set.aggregate(count=Count('nguoithan'))['count']
        print(soluong)
        return soluong

    class Meta:
        model = BaiDangTour
        fields = ["id","created_date","title",'journey', "tags",'pic','state','gia','max','soluongDaDat','avgRate']

class Posts_userSerializer(PostSerializer):  # n user nhieu post
    user_NV = UserSerializer()

    class Meta:
        model = PostSerializer.Meta.model
        fields = ['user_NV'] + PostSerializer.Meta.fields


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj.user
        return {
            "username": user.username,
            "avatar": user.avatar.url if user.avatar else None
        }

    class Meta:
        model = CommentReply
        fields = ['id', 'content', 'created_date', 'user']



class PostDetailSerializer(PostSerializer):
    tags = TagSerializer(many=True)
    pic = ImageSerializer(many=True)
    class Meta:
        model = PostSerializer.Meta.model
        fields = PostSerializer.Meta.fields + ['content', 'tags', 'pic',"active"]

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Rating
        fields = ['id', 'rate', "user"]
