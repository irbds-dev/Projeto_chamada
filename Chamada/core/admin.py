from django.contrib import admin
from .models import Aluno
from .models import Chamada
from .models import Turma

# Register your models here.
admin.site.register(Aluno)
admin.site.register(Chamada)
admin.site.register(Turma)