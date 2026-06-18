"""
vats/serializers.py  —  HelpDesk Pro v2
DRF serializers — correct app references (vats.models, registration.models).
"""
from rest_framework import serializers
from .models import Category, Subcategory, Ticket, Worknote
from registration.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    """Compact user info used inside ticket rows."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'full_name', 'email', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'is_active', 'date_joined',
        ]
        read_only_fields = ['date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()


class CategorySerializer(serializers.ModelSerializer):
    ticket_count = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'ticket_count']

    def get_ticket_count(self, obj):
        return obj.ticket_set.count()


class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Subcategory
        fields = ['id', 'category', 'category_name', 'name']


class WorknoteSerializer(serializers.ModelSerializer):
    commented_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model  = Worknote
        fields = [
            'id', 'ticket', 'type', 'comment',
            'commented_by', 'created_at',
            'field_name', 'old_value', 'new_value',
        ]
        read_only_fields = ['commented_by', 'created_at']


class TicketListSerializer(serializers.ModelSerializer):
    """Compact — used for the ticket table (no worknotes loaded)."""
    created_by   = UserMinimalSerializer(read_only=True)
    assigned_to  = UserMinimalSerializer(read_only=True)
    category_name    = serializers.CharField(source='category.name',    read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    is_sla_breached  = serializers.BooleanField(read_only=True)
    resolution_time_hours = serializers.FloatField(read_only=True)

    class Meta:
        model  = Ticket
        fields = [
            'id', 'number', 'title',
            'priority', 'status',
            'category', 'category_name',
            'subcategory', 'subcategory_name',
            'created_by', 'assigned_to',
            'created_at', 'updated_at',
            'due_by', 'resolved_at',
            'is_sla_breached', 'resolution_time_hours',
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    """Full — used for the ticket detail page (includes worknotes)."""
    created_by   = UserMinimalSerializer(read_only=True)
    assigned_to  = UserMinimalSerializer(read_only=True)
    category_name    = serializers.CharField(source='category.name',    read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    is_sla_breached  = serializers.BooleanField(read_only=True)
    resolution_time_hours = serializers.FloatField(read_only=True)
    age_hours        = serializers.FloatField(read_only=True)
    worknotes        = WorknoteSerializer(source='Worknotes', many=True, read_only=True)

    class Meta:
        model  = Ticket
        fields = [
            'id', 'number', 'title', 'problem_descp',
            'priority', 'status',
            'category', 'category_name',
            'subcategory', 'subcategory_name',
            'created_by', 'assigned_to',
            'created_at', 'updated_at',
            'due_by', 'resolved_at',
            'is_sla_breached', 'resolution_time_hours', 'age_hours',
            'worknotes',
        ]
        read_only_fields = ['number', 'created_by', 'created_at', 'updated_at']
