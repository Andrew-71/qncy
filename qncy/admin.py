from django.contrib import admin

from qncy.models import Question, Answer, QuestionVote, AnswerVote, Tag


class QuestionAdmin(admin.ModelAdmin):
    search_fields = (
        "title",
        "content",
    )
    readonly_fields = ("rating",)
    raw_id_fields = ("author",)

    class AnswerInLine(admin.TabularInline):
        model = Answer
        extra = 0
        raw_id_fields = ("author",)

    class VoteInline(admin.TabularInline):
        model = QuestionVote
        extra = 0
        raw_id_fields = ("user", "question")

    inlines = (
        AnswerInLine,
        VoteInline,
    )


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ("content",)
    readonly_fields = ("rating",)
    raw_id_fields = ("author",)
    list_filter = ("accepted",)

    class VoteInline(admin.TabularInline):
        model = AnswerVote
        extra = 0
        raw_id_fields = ("user", "answer")

    inlines = (VoteInline,)


class QuestionVoteAdmin(admin.ModelAdmin):
    model = QuestionVote
    raw_id_fields = ("user", "question")
    list_filter = ("up",)


class AnswerVoteAdmin(admin.ModelAdmin):
    model = AnswerVote
    raw_id_fields = ("user", "answer")
    list_filter = ("up",)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tag)
admin.site.register(QuestionVote, QuestionVoteAdmin)
admin.site.register(AnswerVote, AnswerVoteAdmin)
