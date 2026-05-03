from rest_framework import serializers

import datetime as dt

from .models import CHOICES, Achievement, AchievementCat, Cat, User, Vaccine, CatVaccination, Reminder


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
        ref_name = 'ReadOnlyUsers'


class AchievementSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Achievement
        fields = ('id', 'name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    color = serializers.ChoiceField(choices=CHOICES)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'achievements', 'owner',
                  'age')
        read_only_fields = ('owner',)

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
    status = serializers.CharField(read_only=True)

    class Meta:
        model = CatVaccination
        fields = '__all__'

    def validate(self, data):
        date_val = data.get('date')
        next_date_val = data.get('next_date')
        cat = data.get('cat')
        vaccine = data.get('vaccine')

        if date_val and next_date_val:
            if next_date_val < date_val:
                raise serializers.ValidationError(
                    {"next_date": "Дата следующей вакцинации должна быть позже даты текущей"}
                )

        if cat and vaccine and date_val:
            existing = CatVaccination.objects.filter(
                cat=cat, vaccine=vaccine, date=date_val
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError(
                    "Уже существует запись о вакцинации этим препаратом для данного кота в эту дату"
                )

        return data


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_date')

    def validate_vaccination(self, value):
        if not CatVaccination.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Указанная вакцинация не существует")
        return value
