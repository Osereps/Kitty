from rest_framework import serializers, viewsets
from rest_framework.validators import UniqueTogetherValidator

import datetime as dt

from .models import CHOICES, Achievement, AchievementCat, Cat, User, Vaccine, CatVaccination


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
        ref_name = 'ReadOnlyUsers'


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    color = serializers.ChoiceField(choices=CHOICES)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'achievements', 'owner',
                  'age')

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Имя кота должно содержать минимум 2 символа")
        return value.strip()

    def validate_birth_year(self, value):
        current_year = dt.datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(f"Год рождения не может быть больше {current_year}")
        if value < 1900:
            raise serializers.ValidationError("Год рождения не может быть меньше 1900")
        return value

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(**validated_data)
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement)
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat)
            return cat
        
class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = '__all__'

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название вакцины должно содержать минимум 3 символа")
        return value.strip()


class CatVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatVaccination
        fields = '__all__'

    def validate(self, data):
        if data.get('date') and data.get('next_date'):
            if data['next_date'] < data['date']:
                raise serializers.ValidationError("Дата следующей вакцинации должна быть позже даты текущей")
        return data
