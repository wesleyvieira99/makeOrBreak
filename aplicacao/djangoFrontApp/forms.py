from django.forms import ModelForm
from .models import Metrics, MetricsValues, Project, Origin
from django.core.exceptions import ValidationError


class MetricsValuesForm(ModelForm):
    class Meta:
        model = MetricsValues
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metrica'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['valor'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['tempo'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['decisao'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['cadastrado_por'].error_messages = {'required': 'Este campo é obrigatório.'}

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        try:
            float(valor)
        except ValueError:
            raise ValidationError("Este campo aceita somente números.")
        return valor


class MetricsForm(ModelForm):
    class Meta:
        model = Metrics
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].error_messages = {'required': 'Este campo é obrigatório.'}

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if nome.isnumeric() or len(nome) > 100:
            raise ValidationError("O nome não pode ser numérico ou maior que 100 caracteres")
        else:
            return nome


class ProjetosForm(ModelForm):
    class Meta:
        model = Project
        fields = 'nome', 'descricao'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['descricao'].error_messages = {'required': 'Este campo é obrigatório.'}

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if nome.isnumeric() or len(nome) > 100:
            raise ValidationError("O nome não pode ser numérico ou maior que 100 caracteres")
        else:
            return nome

    def clean_descricao(self):
        descricao = self.cleaned_data['descricao']
        if descricao.isnumeric() or len(descricao) > 500:
            raise ValidationError("A categoria não pode ser numérica ou maior que 500 caracteres")
        else:
            return descricao


class OriginsForm(ModelForm):
    class Meta:
        model = Origin
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['descricao'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['tecnologia'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['endpoint'].error_messages = {'required': 'Este campo é obrigatório.'}
        self.fields['responsavel'].error_messages = {'required': 'Este campo é obrigatório.'}

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if nome.isnumeric() or len(nome) > 100:
            raise ValidationError("O nome não pode ser numérico ou maior que 100 caracteres")
        else:
            return nome

    def clean_descricao(self):
        descricao = self.cleaned_data['descricao']
        if descricao.isnumeric() or len(descricao) > 500:
            raise ValidationError("A descrição não pode ser numérica ou maior que 500 caracteres")
        else:
            return descricao

    def clean_tecnologia(self):
        tecnologia = self.cleaned_data['tecnologia']
        if tecnologia.isnumeric() or len(tecnologia) > 100:
            raise ValidationError("A tecnologia informada não pode ser numérica ou maior que 100 caracteres")
        else:
            return tecnologia

    def clean_endpoint(self):
        endpoint = self.cleaned_data['endpoint']
        if endpoint.isnumeric() or len(endpoint) > 500:
            raise ValidationError("O endpoint informado não pode ser numérico ou maior que 500 caracteres")
        else:
            return endpoint

    def clean_responsavel(self):
        responsavel = self.cleaned_data['responsavel']
        if responsavel.isnumeric() or len(responsavel) > 100:
            raise ValidationError("O e-mail do responsável não pode ser numérico ou maior que 100 caracteres")
        else:
            return responsavel
