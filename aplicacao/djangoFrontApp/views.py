import random
import string

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import logout

from .models import Metrics, MetricsValues, Project, Origin, Ratings, Train, Prediction, PasswordChanges
from .forms import MetricsForm, MetricsValuesForm, ProjetosForm, OriginsForm
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .filters import MetricsFilter, RatingFilter
from django.core.exceptions import ObjectDoesNotExist

from django.urls import reverse

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib
import os.path
import csv

import io
import base64
import seaborn as sns
import matplotlib.pyplot as plt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.http import JsonResponse
import json


def redirect_to_home(request):
    return redirect('home')


#--------------Home para casos sem predição
@login_required
def home(request):
    projects = Project.objects.all()
    metricshome = ''
    projectselected = False

    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        if project_id:
            metricshome = Metrics.objects.filter(projeto=project_id)
            projectselected = True
        else:
            return redirect(reverse('home') + '?status_toast=erro' + '&mensagem_toast=Projeto não foi selecionado para visualizar as métricas oriundas!')

    context = {
        'projects': projects,
        'projectselected': projectselected,
        'metrics': metricshome,
        'nome_usuario': request.user.username,
    }
    return render(request, 'home.html', context)


#--------------Views para sugestões
@login_required
def rating(request):
    if request.method == "POST":
        rating_user = request.POST.get('rating_user')
        rating_message = request.POST.get('rating_message')
        print(rating_user, rating_message)
        if rating_message == '':
            return redirect(reverse('rating') + '?status_toast=erro' + '&mensagem_toast=Não é possível enviar uma mensagem vazia! Tente novemente.')
        else:
            try:
                rating = Ratings(user_id=rating_user, comment=rating_message)
                print(rating)
                rating.save()
                return redirect(reverse('rating') + '?status_toast=sucesso' + '&mensagem_toast=Comentário incluído com sucesso!')
            except:
                return redirect(reverse('rating') + '?status_toast=erro' + '&mensagem_toast=Erro ao incluir comentário, tente novamente!')
    else:
        ratings = Ratings.objects.order_by('-id')
        ratingsFilter = RatingFilter(request.GET, queryset=ratings)

        # Resto do código...
        paginator = Paginator(ratingsFilter.qs, 5)
        # Obtenha o número da página atual da solicitação
        pagina = request.GET.get('pagina')
        # Obtenha os objetos a serem exibidos na página atual
        ratings_paginadas = paginator.get_page(pagina)

        user = request.user
        user_id = user.id
        user_name = user.username
        return render(request, 'rating.html', {'nome_usuario': request.user.username,'ratings_paginadas': ratings_paginadas,'ratings': ratings,'user_id': user_id, 'user_name': user_name })


def rating_exclude(request, id):
    try:
        print(id)
        print(request.user.id)
        rating = Ratings.objects.filter(id=id)
        rating.delete()
        return redirect(reverse('rating') + '?status_toast=sucesso' + '&mensagem_toast=Comentário excluído com sucesso!')
    except:
        return redirect(reverse('rating') + '?status_toast=erro' + '&mensagem_toast=Erro akko excluir comentário, tente novamente!')



#--------------Views para gestão de Origens
@login_required
def origins(request):
    origins = Origin.objects.all()
    if request.method == "POST":
        originsForm = OriginsForm(request.POST)
        if originsForm.is_valid():
            try:
                originsForm.save()
                # mostra mensagem de sucesso
                return redirect(reverse('origins') + '?status_toast=sucesso' + '&mensagem_toast=Origem criada com sucesso!')
            except:
                return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=Não foi possível criar a origem, tente novamente!')
        else:
            return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=Cadastro preenchido incorretamente, tente novamente!')

    else:
        originsForm = OriginsForm()
    return render(request, 'origins.html', {'nome_usuario': request.user.username,'originsForm': originsForm, 'origins': origins})


@login_required
def viewmetricsorigin(request, id):
    try:
        metrics = Metrics.objects.filter(origin=id)
        print(metrics)
        metrics_data = []
        if metrics:
            for metric in metrics:
                print(metric)
                countDados = metric.metricsvalues_set.count()
                print(countDados)
                project = metric.projeto.nome
                print(project)

                metrics_data.append({
                    'metric_name': metric.nome,
                    'project_name': project,
                    'countDados': countDados
                })
            print(metrics_data)
            return JsonResponse(metrics_data, safe=False)
        else:
            return JsonResponse([], safe=False)

    except Metrics.DoesNotExist:
        return JsonResponse([], status=404)


@login_required
def originsExcludeAll(request):
    if request.method == "POST":
        id = request.POST.get('originId')
        origin = Origin.objects.get(id=id)
        print(id)
        try:
            origin.delete()
            return redirect(reverse('origins') + '?status_toast=sucesso' + '&mensagem_toast=Origem e todas suas possíveis métricas atreladas excluídas com sucesso!')
        except Origin.DoesNotExist:
            return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=A Origem que está tentando excluir não existe')
        except Exception as e:
            return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=Erro ao deletar Origem! Tente novamente!')
    else:
        return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=Erro ao deletar Origem! Tente novamente!')


@login_required
def originsExcludeSub(request):
    if request.method == "POST":
        originforExclude = request.POST.get('originId')
        originforReplace = request.POST.get('replacement_select')

        metrics_to_update = Metrics.objects.filter(origin=originforExclude)

        if originforReplace == originforExclude:
            return redirect(reverse('origins') + '?status_toast=warning' + '&mensagem_toast=Não é possível excluir origem e substituir com a mesma origem já deletada. Tente substituição com outra origem!')
        else:
            if metrics_to_update.exists():
                try:
                    metrics_to_update.update(origin=originforReplace)
                    Origin.objects.filter(id=originforExclude).delete()
                    return redirect(reverse('origins') + '?status_toast=sucesso' + '&mensagem_toast=Antiga origem excluída e suas métricas foram atribuídas à nova origem!')
                except Exception as e:
                    return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=Erro ao deletar Origem! Tente novamente!')
            else:
                return redirect(reverse('origins') + '?status_toast=warning' + '&mensagem_toast=A Origem que está tentando excluir não está atribuída à uma métrica para ser substituída!')
    else:
        return redirect(reverse('origins') + '?status_toast=erro' + '&mensagem_toast=Erro ao deletar Origem! Tente novamente!')


#--------------Views para gestão de Projetos
@staff_member_required(login_url='home')
@login_required
def projetos(request):
    projects = Project.objects.all()
    users = User.objects.all()
    if request.method == "POST":
        projetosForm = ProjetosForm(request.POST)
        if projetosForm.is_valid():
            try:
                projetosForm.save()
                # mostra mensagem de sucesso
                return redirect(reverse('projetos') + '?status_toast=sucesso' + '&mensagem_toast=Projeto salvo!')
            except:
                return redirect(reverse('projetos') + '?status_toast=erro' + '&mensagem_toast=Não foi possível salvar projeto! Tente novamente!')
    else:
        projetosForm = ProjetosForm()
    return render(request, 'projetos.html', {'nome_usuario': request.user.username,'projetosForm': projetosForm, 'users': users, 'projects': projects})


@staff_member_required(login_url='home')
@login_required
def usuarioprojetoassociar(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('project_id')
            user_id = request.POST.get('user_id')

            projeto = Project.objects.get(pk=project_id)
            usuario = User.objects.get(pk=user_id)

            try:
                projeto.user.get(pk=user_id)
                return redirect(reverse('projetos') + '?status_toast=erro' + '&mensagem_toast=Usuário já associado ao projeto!')
            except ObjectDoesNotExist:
                projeto.user.add(usuario)
                return redirect(reverse('projetos') + '?status_toast=sucesso' + '&mensagem_toast=Usuário associado ao projeto com sucesso!')

        except (Project.DoesNotExist, User.DoesNotExist):
            return redirect(reverse('projetos') + '?status_toast=erro' + '&mensagem_toast=Projeto e usuário não existem!')


@staff_member_required(login_url='home')
@login_required
def consultausuarioprojeto(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        users = project.user.all()

        user_data = [{'id': user.id, 'username': user.username} for user in users]

        return JsonResponse(user_data, safe=False)
    except Project.DoesNotExist:
        return JsonResponse([], safe=False)

@staff_member_required(login_url='home')
@login_required
def usuarioprojetoretirar(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('project_id')
            userselect = request.POST.get('userselect')

            projeto = Project.objects.get(pk=project_id)
            usuario = User.objects.get(pk=userselect)

            projeto.user.remove(usuario)

            return redirect(reverse('projetos') + '?status_toast=sucesso' + '&mensagem_toast=Usuário retirado do projeto com sucesso!')

        except:
            return redirect(reverse('projetos') + '?status_toast=erro' + '&mensagem_toast=Erro ao retirar usuário do projeto, tente novamente!')

@staff_member_required(login_url='home')
@login_required
def encerrarprojeto(request, id):
    try:
        projeto = Project.objects.get(id=id)
        projeto.delete()
        return redirect(reverse('projetos') + '?status_toast=sucesso' + '&mensagem_toast=Projeto encerrado com sucesso!')
    except Project.DoesNotExist:
        return HttpResponse('A instância de Project não existe')
    except Exception as e:
        return HttpResponse('Erro ao encerrar o projeto: {}'.format(str(e)))

#--------------Gerenciamento de users

@staff_member_required(login_url='home')
def admin_users(request):
    usuarios = User.objects.all()
    context = {
        'users': usuarios,
        'nome_usuario': request.user.username
    }
    return render(request, 'users.html', context)

@staff_member_required(login_url='home')
def tornar_admin(request, usuario_id):
    try:
        usuario = get_object_or_404(User, id=usuario_id)
        usuario.is_staff = True
        usuario.save()
        return redirect(reverse('admin_users') + '?status_toast=sucesso' + '&mensagem_toast=Usuário ajustado para admin do sistema!')
    except Exception as e:
        return redirect(reverse('admin_users') + '?status_toast=erro' + '&mensagem_toast=Erro ao tornar o usuário admin, tente novamente!')


@staff_member_required(login_url='home')
def remover_admin(request, usuario_id):
    try:
        usuario = get_object_or_404(User, id=usuario_id)
        usuario.is_staff = False
        usuario.save()
        return redirect(reverse('admin_users') + '?status_toast=sucesso' + '&mensagem_toast=Usuário ajustado para usuário padrão do sistema!')
    except Exception as e:
        return redirect(reverse('admin_users') + '?status_toast=erro' + '&mensagem_toast=Erro ao tornar o usuário à user padrão, tente novamente!')


@staff_member_required(login_url='home')
def excluir_usuario(request, usuario_id):
    try:
        usuario = get_object_or_404(User, id=usuario_id)
        usuario.delete()
        return redirect(reverse('admin_users') + '?status_toast=sucesso' + '&mensagem_toast=Usário excluído do sistema com sucesso!')
    except Exception as e:
        return redirect(reverse('admin_users') + '?status_toast=erro' + '&mensagem_toast=Erro ao excluir usuário do sistema, tente novamente!')


@staff_member_required(login_url='home')
def selecionar_senha(request, usuario_id):
    try:
        usuario = get_object_or_404(User, id=usuario_id)
        nova_senha = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(8))
        usuario.set_password(nova_senha)

        print(nova_senha)
        usuario.save()

        pwd = PasswordChanges(new_pwd=nova_senha, date=timezone.now().date(), user_id=usuario_id)
        pwd.save()

        mensagem_toast = 'Nova senha do usuário: {}'.format(nova_senha)
        return redirect(reverse('admin_users') + '?status_toast=sucesso' + '&mensagem_toast=' + mensagem_toast)
    except Exception as e:
        return redirect(reverse('admin_users') + '?status_toast=erro' + '&mensagem_toast=Erro ao setar nova senha ao usuário do sistema, tente novamente!')


#--------------Visualizar predições realizadas
def viewpred(request):
    preds = Prediction.objects.all()

    # Cria a resposta HTTP e adiciona o nome do arquivo
    response = HttpResponse(content_type='text/csv')
    nome_arquivo = f'predicoes_realizadas.csv'
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    # Cria o objeto writer do CSV e escreve os dados
    writer = csv.writer(response)
    writer.writerow(['value_informed', 'time_informed', 'result', 'metric_id'])
    for i in preds:
        writer.writerow([i.value_informed, i.time_informed, i.result, i.metric_id])
    return response

#--------------Visualizar treinos realizados
def viewtrain(request):
    trains = Train.objects.all()

    # Cria a resposta HTTP e adiciona o nome do arquivo
    response = HttpResponse(content_type='text/csv')
    nome_arquivo = f'treino_realizados.csv'
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    # Cria o objeto writer do CSV e escreve os dados
    writer = csv.writer(response)
    writer.writerow(['acuracia', 'data', 'user_id'])
    for i in trains:
        writer.writerow([i.accuracy, i.date, i.user_id])
    return response
#--------------Execução e operacionalização de treinos e modelo neural

def exec_train():
    metrics_values = MetricsValues.objects.all()
    # Transformar os dados em um dataframe do Pandas
    df = pd.DataFrame([(m.metrica_id, m.valor, m.tempo, m.decisao) for m in metrics_values],
                      columns=['metrica_id', 'valor', 'tempo', 'decisao'])

    # Separar as variáveis independentes (X) da variável dependente (y)
    X = df.drop('decisao', axis=1)
    y = df['decisao']

    # Dividir os dados em conjuntos de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Criar o modelo DecisionTree
    model = DecisionTreeClassifier()

    # Treinar o modelo com os dados de treino
    model.fit(X_train, y_train)

    # Fazer previsões com os dados de teste
    y_pred = model.predict(X_test)

    # Calcular a acurácia do modelo
    accuracy = accuracy_score(y_test, y_pred) * 100
    print(f'Acurácia: {accuracy:.2f}')



    return model, accuracy


def train_model(request):
    if request.method == 'POST':
        try:
            model, accuracy = exec_train()
            # Salvar o modelo treinado em um arquivo para uso futuro
            joblib.dump(model, 'model.joblib')

            current_date = timezone.now().date()
            user = request.user
            train = Train(accuracy=accuracy, date=current_date, user=user)
            train.save()
            print('treinado com sucesso!')

            # obter a rota atual
            url_name = request.resolver_match.url_name
            # redirecionar para a view correspondente com o parâmetro "mensagem_toast"
            if url_name == 'home':
                return redirect(reverse('home') + '?status_toast=sucesso' + '&mensagem_toast=Modelo treinado com sucesso!')
            else:
                # redirecionar para a metric-train por padrão se a rota atual não estiver mapeada
                return redirect(reverse('metric-train') + '?status_toast=sucesso' + '&mensagem_toast=Modelo treinado com sucesso!')

        except:
            # Retorne uma mensagem de erro para o usuário
            return redirect(reverse('metric-train') + '?status_toast=erro' + '&mensagem_toast=Falha ao treinar o modelo, tente novamente!')
    else:
        return render(request, 'metric-train.html')

@login_required
def home_prediction(request):
    projects = Project.objects.all()

    # Carregar o modelo treinado a partir do arquivo
    if not os.path.exists('model.joblib'):
        try:
            model, accuracy = exec_train()
            # Salvar o modelo treinado em um arquivo para uso futuro
            joblib.dump(model, 'model.joblib')
            print('treinado com sucesso!')
        except Exception as e:
            return redirect(reverse('metric-train') + '?status_toast=erro' + '&mensagem_toast=Modelo ainda não treinado! Tente treinar o modelo antes de realizar uma predição!')

    model = joblib.load('model.joblib')

    ############APÓS O TREINO, E MEDIÇÃO DA ACURÁCIA, FAZER PREDIÇÃO COM DADOS ENVIADOS PELO USUÁRIO#####
    if request.method == 'POST':
        try:
            # Pegue os dados do usuário do formulário
            metrica_id = request.POST.get('metrica_id')
            valor = request.POST.get('valor')
            tempo = request.POST.get('tempo')

            user = request.user

            countDados = MetricsValues.objects.filter(metrica_id=metrica_id).count()
            if countDados == 0:
                return redirect(reverse('home') + '?status_toast=warning' + '&mensagem_toast=Modelo sem métricas cadastradas. Cadastre métricas e treine o modelo antes de realizar uma predição!')

            # Crie um objeto MetricsValues a partir dos dados do usuário
            metrica = MetricsValues(metrica_id=metrica_id, valor=valor, tempo=tempo, cadastrado_por=user)

            # Adicione o objeto MetricsValues a uma lista de objetos
            data = [metrica]
            # Crie um dataframe a partir da lista de objetos
            df = pd.DataFrame([vars(i) for i in data])
            # Faça a predição utilizando o modelo DecisionTree
            prediction = model.predict(df[['metrica_id', 'valor', 'tempo']])
            # Converta a predição para um formato legível (0 ou 1)
            decisao_prediction = prediction
            # Calcule a acurácia da predição
            print(decisao_prediction)

            metrics = Metrics.objects.all()
            metricsValues = MetricsValues.objects.filter(metrica_id=metrica_id).values('valor', 'tempo', 'decisao')
            # Crie um novo dataframe contendo as variáveis valor, tempo e decisão
            df_plot = pd.DataFrame(list(metricsValues.values('valor', 'tempo', 'decisao')))

            print(metricsValues)

            execucacaoTreino = exec_train()
            accuracy = f'{execucacaoTreino[1]:.2f}'

            # Cria o gráfico de Pairplot
            sns.set(style="ticks")
            sns.pairplot(df_plot[['valor', 'tempo', 'decisao']], height=2.5)
            # Salve a figura em memória como um objeto BytesIO
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            # Converta a imagem em formato base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Salvando histórico da predição
            print(valor, tempo, int(decisao_prediction), metrica_id)
            pred = Prediction(value_informed=valor, time_informed=tempo, result=int(decisao_prediction), metric_id=metrica_id)
            pred.save()

            data= {
                'decisao_prediction': decisao_prediction,
                'accuracy': accuracy,
                'image_base64': image_base64,
                'metrica_id': metrica_id,
                'valor': valor,
                'tempo': tempo,
                'metrics': metrics,
                'nome_usuario': request.user.username,
                'projects': projects
            }

            # Renderize o template home e passe o contexto para ele com os dados
            return render(request, 'home.html', data)
        except Exception as e:
            # Retorne uma mensagem de erro para o usuário
            return redirect(reverse('home') + '?status_toast=erro&mensagem_toast=Não foi possível realizar a predição. Tente novamente! Persistindo o erro, contate o administrador.')
    else:
        return render(request, 'home.html', {'projects': projects})


#--------------Gestão de Métricas

def infomodal(request):
    if request.method == 'POST':
        form = MetricsValuesForm(request.POST)
        if form.is_valid():
            try:
                form.instance.cadastrado_por = request.user.username
                form.save()
                # Chamar a função para treinar o modelo no início do aplicativo
                model = form.instance
                # mostra mensagem de sucesso
                return redirect(reverse('metricsTrainSelected') + '?status_toast=sucesso' + '&mensagem_toast=Informações cadastradas na métrica com sucesso!')
            except Exception as e:
                return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Falha no cadastro das informações, tente novamente!')
        else:
            return redirect(reverse('metricsTrainSelected') + '?status_toast=warning' + '&mensagem_toast=Formulário não está valido! Preencha-o novamente!')

    else:
        return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '?mensagem_toast=Revise o que fez, algo está errado!')


def contador():
    metrica_counts = MetricsValues.objects.values('metrica_id').annotate(total=Count('metrica_id'))
    return metrica_counts





def metricsTrainSelected(request):
    try:
        user = request.user
        projects = Project.objects.filter(user=user)
        #dado de projeto vindo da tela inicial de metric train e das proprias telas de metricselected
        if request.POST.get('formProject'):
            selectedProject = request.POST.get('formProject')
        #se tiver um projeto na sessão do usuário pegar de lá, quer dizer que guardou porque acabou de criar uma e redireciona para o projeto que acabou de ter uma metrica criada
        elif request.session.get('selected_project'):
            selectedProject = request.session.get('selected_project')
        #qualquer outra requisição de fora, como direto pelo browser, mas somente o primeiro que o usuario está associado
        else:
            first_project = Project.objects.filter(user=user).first()
            selectedProject = first_project.id

        completeProject = Project.objects.get(id=selectedProject)
        formName = request.POST.get('formName')

        metrics = Metrics.objects.filter(projeto=selectedProject)


        if request.POST.get('plus') == 'plus_button':
                # Passar os valores para o filtro
                typeFilter = MetricsFilter(request.GET, queryset= Metrics.objects.filter(nome__icontains=formName, projeto=selectedProject).select_related('origin').values('id', 'nome', 'projeto', 'origin__nome'))
        elif request.POST.get('minus') == 'minus_button':
                # filtro vazio
                typeFilter = MetricsFilter(request.GET, queryset=Metrics.objects.filter(projeto=selectedProject).select_related('origin').values('id', 'nome', 'projeto', 'origin__nome'))
        else:
            # filtro
            typeFilter = MetricsFilter(request.GET, queryset=Metrics.objects.filter(projeto=selectedProject).select_related('origin').values('id', 'nome', 'projeto', 'origin__nome'))

        # Resto do código...
        paginator = Paginator(typeFilter.qs, 5)
        # Obtenha o número da página atual da solicitação
        pagina = request.GET.get('pagina')
        # Obtenha os objetos a serem exibidos na página atual
        metrics_paginadas = paginator.get_page(pagina)
        print(metrics_paginadas)

        metricsValues = MetricsValues.objects.all()
        formTrain = MetricsValuesForm()
        metricsIdcount = contador()

        data = {
            'selectedProject': selectedProject,
            'metrics_paginadas': metrics_paginadas,
            'formTrain': formTrain,
            'metricsValues': metricsValues,
            'metricsIdcount': metricsIdcount,
            'nome_usuario': request.user.username,
            'completeProject': completeProject,
            'projects': projects,
            'typeFilter': typeFilter,
            'metrics': metrics,
            'user': user
        }

        return render(request, 'metric-train.html', data)
    except:
        return redirect(reverse('metric-train') + '?status_toast=erro' + '&mensagem_toast=Erro na solicitação de informações do projeto!')


@login_required
def metricsTrain(request):
    user = request.user
    projects = Project.objects.filter(user=user)

    selectedProject = None
    return render(request, 'metric-train.html', {'nome_usuario': request.user.username,'selectedProject': selectedProject, 'projects': projects, 'user': user})

@login_required
def metricsCreate(request):
    user = request.user
    projects = Project.objects.filter(user=user)
    origins = Origin.objects.all()
    if request.method == "POST":
        form = MetricsForm(request.POST)
        #armazenando em cookies do usuário o projeto que foi criado para mostrar na view de MetricsSelected o projeto utilizado
        selectedProject = request.POST.get('projeto')
        request.session['selected_project'] = selectedProject
        request.session.save()
        if form.is_valid():
            try:
                form.save()
                # mostra mensagem de sucesso
                return redirect(reverse('metricsTrainSelected') + '?status_toast=sucesso' + '&mensagem_toast=Métrica criada com sucesso!')
            except:
                return redirect(reverse('metric-create') + '?status_toast=erro' + '&mensagem_toast=Erro no preenchimento das informações da métrica, tente novamente!')
    else:
        form = MetricsForm()
    return render(request, 'metric-create.html', {'form': form, 'nome_usuario': request.user.username, 'origins': origins , 'projects': projects})


@login_required
def metricsDelete(request, id):
    metric = Metrics.objects.get(id=id)
    try:
        metric.delete()
        return redirect(reverse('metricsTrainSelected') + '?status_toast=sucesso' + '&mensagem_toast=Métrica deletada com sucesso!')
    except Metrics.DoesNotExist:
        return HttpResponse('A instância de Metrics não existe')
    except Exception as e:
        return HttpResponse('Erro ao deletar a instância de Metrics: {}'.format(str(e)))

#--------------Autenticação e gestão do sistema

@login_required
def handlerNotFound(request, exception):
    return render(request, "handlerNotFound.html")

#Deixando o login required so para as paginas, o que é chamdo dentro dela já está garantido pela segurança da propria pagina em si
# AUTENTICAÇÃO E REGISTRO /////////////


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login



def register(request):
    if request.method == "POST":
        email = request.POST.get('inputEmail')
        username = request.POST.get('inputUser')
        password = request.POST.get('inputPwd')

        if not username or not email or not password:
            return redirect(reverse('register') + '?mensagem_toast=authErro')
        else:
            user = User.objects.filter(username=username).first()
            if user:
                return redirect(reverse('enter') + '?mensagem_toast=authWarning')
            else:
                user = User.objects.create_user(username, email, password)
                user.save()
                return redirect(reverse('enter') + '?mensagem_toast=authSucesso')
    else:
        return render(request, 'auth/register.html')


def enter(request):
    if request.method == "POST":
        inputUser = request.POST['inputUser']
        inputPwd = request.POST['inputPwd']
        user = authenticate(request, username=inputUser, password=inputPwd)

        if user is None:
            return redirect(reverse('enter') + '?mensagem_toast=authErro')
        else:
            login(request, user)
            return redirect('home')
    else:
        return render(request, 'auth/enter.html')

@login_required
def upload_csv(request):
    try:
        if request.method == 'POST' and request.FILES['csv_file']:
            metrica_id = request.POST['metrica_id']
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                print("não é um CSV")
                return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Arquivo não é um CSV', status=400)
            else:
                if request.POST['delimiter'] == "virgula":
                    df = pd.read_csv(csv_file, delimiter=',')
                elif request.POST['delimiter'] == "pontoevirgula":
                    df = pd.read_csv(csv_file, delimiter=';')
                else:
                    return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Erro na escolha do delimitador',status=400)
                try:
                    header = df.columns.tolist()
                    if header != ['valor', 'decisao', 'tempo']:
                        print("não é um CAMPO aceito")
                        print(header)
                        return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=CSV fora do formato ou padrão. Tente novamente!',status=400)
                    else:
                        for index, row in df.iterrows():
                            if all(str(x).isdigit() for x in row):
                                infosMetric = MetricsValues(
                                    valor=row[0],
                                    decisao=row[1],
                                    metrica_id=metrica_id,
                                    tempo=row[2],
                                    cadastrado_por= request.user.username
                                )
                                infosMetric.save()
                            else:
                                print("não é iterou legal nos valores")
                                return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Erro ao ler arquivo CSV em seus dados. Possivelmente algum dado não é número',status=400)
                        return redirect(reverse('metricsTrainSelected') + '?status_toast=sucesso' + '&mensagem_toast=Dados lidos via CSV com sucesso!')

                except csv.Error:
                    print("erro ao ler o CSV")
                    return redirect(reverse(
                        'metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Erro ao ler arquivo CSV em seus dados. Tente novamente!',status=400)
        print("erro no envio do CSV")
        return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Erro ao ler arquivo CSV em seus dados.',status=400)
    except Exception as e:
        return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Erro ao ler arquivo CSV em seus dados.',status=500)


@login_required
def listInfo(request, id):
    infoMetrics = MetricsValues.objects.filter(metrica_id=id)


    context = {
        'infoMetrics': infoMetrics,
        'nome_usuario': request.user.username

    }
    return render(request, 'list-info.html', context)

@login_required
def excluirInfos(request):
    if request.method == 'POST':
        valores_selecionados = request.POST.get('valores_selecionados', '').split(',')
        metric_id = request.POST.get('metrica_id')

        if len(valores_selecionados) == 1 and valores_selecionados[0] == '':
            return redirect(reverse('list-info', args=[metric_id]) + '?status_toast=erro' + '&mensagem_toast=Nenhuma métrica selecionada para exclusão!')
        else:
            try:
                print(valores_selecionados, metric_id)

                for valor in valores_selecionados:
                    infosDelete = MetricsValues.objects.get(id=valor, metrica_id=metric_id)
                    infosDelete.delete()

                return redirect(reverse('list-info', args=[metric_id]) + '?status_toast=sucesso' + '&mensagem_toast=Informações da métrica selecionadas foram excluídas com sucesso!',)
            except Exception as e:
                return redirect(reverse('list-info', args=[metric_id]) + '?status_toast=erro' + '&mensagem_toast=Erro ao tentar excluir as informações selecionadas. Tente novamente!',)
    else:
        return redirect(reverse('metricsTrainSelected') + '?status_toast=erro' + '&mensagem_toast=Erro! Tente novamente.')





def download_csv(request, id):
    infoMetrics = MetricsValues.objects.filter(metrica_id=id)

    # Cria a resposta HTTP e adiciona o nome do arquivo
    response = HttpResponse(content_type='text/csv')
    nome_arquivo = f'dados_{id}.csv'
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    # Cria o objeto writer do CSV e escreve os dados
    writer = csv.writer(response)
    writer.writerow(['valor', 'decisao', 'tempo', 'cadastrado_por'])
    for i in infoMetrics:
        writer.writerow([i.valor, i.decisao, i.tempo, i.cadastrado_por])
    return response




@login_required
def sair_view(request):
    logout(request)
    return redirect('enter')
