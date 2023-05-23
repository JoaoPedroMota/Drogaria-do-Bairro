from rest_framework.views import exception_handler
from loja.models import Categoria

def categorias_nao_pai():
    categorias_com_pai = Categoria.objects.filter(categoria_pai__isnull=False)
    pais_ids = categorias_com_pai.values_list('categoria_pai', flat=True)
    categorias_nao_pai = Categoria.objects.exclude(id__in=pais_ids)
    return categorias_nao_pai





def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['detail'] = response.data.get('detail', str(exc))

    return response