from django.contrib import admin

from qncy.models import Question, Answer, QuestionVote, AnswerVote, Tag

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['title','content']
    readonly_fields=('rating',)

    class AnswerInLine(admin.TabularInline):
        model = Answer

    class VoteInline(admin.TabularInline):
        model = QuestionVote
    
    inlines = (AnswerInLine, VoteInline, )

class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['content']
    readonly_fields=('rating',)

    class VoteInline(admin.TabularInline):
        model = AnswerVote
    
    inlines = (VoteInline, )

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tag)
admin.site.register(QuestionVote)
admin.site.register(AnswerVote)
