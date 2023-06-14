import django_filters
from .models import Metrics, Ratings


class MetricsFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')
    projeto = django_filters.CharFilter(lookup_expr='icontains')
    origin = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Metrics
        fields = ['nome', 'projeto', 'origin']


class RatingFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    comment = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ratings
        fields = ['user', 'comment']
