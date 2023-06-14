from django.urls import path
from . import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.redirect_to_home),
    path('home', views.home, name='home'),
    path('rating', views.rating, name='rating'),
    path('viewtrain', views.viewtrain, name='viewtrain'),
    path('viewpred', views.viewpred, name='viewpred'),
    path('admin_users', views.admin_users, name='admin_users'),
    path('tornar_admin/<int:usuario_id>/', views.tornar_admin, name='tornar_admin'),
    path('remover_admin/<int:usuario_id>/', views.remover_admin, name='remover_admin'),
    path('excluir_usuario/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('selecionar_senha/<int:usuario_id>/', views.selecionar_senha, name='selecionar_senha'),
    path('rating_exclude/<int:id>', views.rating_exclude, name='rating_exclude'),
    path('home/<int:project_id>', views.home, name='home'),
    path('projetos', views.projetos, name='projetos'),
    path('usuarioprojetoassociar', views.usuarioprojetoassociar, name='usuarioprojetoassociar'),
    path('usuarioprojetoretirar', views.usuarioprojetoretirar, name='usuarioprojetoretirar'),
    path('consultausuarioprojeto/<int:project_id>', views.consultausuarioprojeto, name='consultausuarioprojeto'),
    path('encerrarprojeto/<int:id>', views.encerrarprojeto, name='encerrarprojeto'),
    path('home_prediction', views.home_prediction, name='home_prediction'),
    path('metric-train', views.metricsTrain, name='metric-train'),
    path('metricsTrainSelected', views.metricsTrainSelected, name='metricsTrainSelected'),
    path('infomodal', views.infomodal, name='infomodal'),
    path('metric-create', views.metricsCreate, name='metric-create'),
    path('metric-delete/<int:id>', views.metricsDelete, name='metric-delete'),
    path('list-info/<int:id>', views.listInfo, name='list-info'),
    path('excluirInfos', views.excluirInfos, name='excluirInfos'),
    path('origins', views.origins, name='origins'),
    path('originsExcludeAll', views.originsExcludeAll, name='originsExcludeAll'),
    path('originsExcludeSub', views.originsExcludeSub, name='originsExcludeSub'),
    path('viewmetricsorigin/<int:id>', views.viewmetricsorigin, name='viewmetricsorigin'),
    path('download_csv/<int:id>', views.download_csv, name='download_csv'),
    path('train_model', views.train_model, name='train_model'),
    path('register', views.register, name='register'),
    path('enter', views.enter, name='enter'),
    path('sair/', views.sair_view, name='sair'),
    path('upload_csv', views.upload_csv, name='upload_csv')

]


