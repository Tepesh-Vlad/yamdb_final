import re
from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator, ValidationError

from api_yamdb.reviews.models import Category, Comment, Genre, Review, Title, User


def validate_username(value):
    if (('username' in value and not re.compile(
            r'[\w.@+-]+$').match(value['username']))
            or ('username' in value and value['username'].lower() == 'me')):
        raise serializers.ValidationError('Недопустимое имя пользователя!')


def validate_year(value):
    if 'year' in value and value['year'] > datetime.now().year:
        raise serializers.ValidationError(
            f'The title cannot be created in the future'
            f'( year <= {datetime.now().year})')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        validators = [validate_username]
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        validators = [validate_username]
        fields = ('username', 'email')


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    score = serializers.IntegerField(min_value=1, max_value=10)
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'pub_date', 'author']

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title = self.context['view'].kwargs.get('title_id')
        if (request.method == 'POST'
           and Review.objects.filter(title=title, author=author).exists()):
            raise ValidationError(
                {'title': 'Нельзя добавить более одного отзыва'})
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id', 'pub_date', 'author']


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('id', 'name', 'year', 'rating',
                            'description', 'genre', 'category')
        validators = [validate_year]

    def get_rating(self, obj):
        return Review.objects.filter(title=obj).aggregate(
            Avg('score'))['score__avg']


class WriteTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        validators = [validate_year]
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
