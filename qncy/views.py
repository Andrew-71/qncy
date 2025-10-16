from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from qncy.models import Question, Tag, User, QuestionForm, Answer

from django.db.models import Count

from django.contrib.auth import logout

from vkhw import settings

def paginator_page(request, objects):
    # There's probably a more pythonistic way to do this
    page = 1
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        pass
    page_size = 20
    try:
        page_size = int(request.GET.get("pagesize", 20))
    except ValueError:
        pass
    paginator = Paginator(objects, page_size)
    return paginator.get_page(page)

def common_context():
    top_tags = Tag.objects.annotate(
        uses=Count('question')).order_by('-uses')[:20]
    top_users = User.objects.annotate( # FIXME: this is NOT what we want.
        rating=Count('answer')).order_by('-rating')[:10]

    return {
        "common": {
            "top_tags": top_tags,
            "top_users": top_users
        }
    }

def index(request):
    # TODO: sorting?
    latest_question_list = Question.objects.order_by("-created_at").annotate(
        answers=Count('answer'),
    )
    context = {
        "page_obj": paginator_page(request, latest_question_list),
    }
    return render(request, "qncy/index.html", context | common_context())

def question(request, question_id):
    try:
        question = Question.objects.annotate(
            answers=Count('answer'),
        ).get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")

    answers_list = Answer.objects.filter(question=question).order_by("-rating")
    context = {
        "question": question,
        "page_obj": paginator_page(request, answers_list),
    }

    return render(request, "qncy/question.html", context | common_context())

def tag(request, tag_name):
    try:
        tag = Tag.objects.get(name=tag_name)
    except Tag.DoesNotExist:
        raise Http404("Tag does not exist")

    return render(request, "qncy/question.html", {"question": question} | common_context())

def logout_view(request):
    logout(request)
    return render(request, "qncy/logged_out.html", common_context())

def ask(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    
    question = Question(author=request.user)
    form = QuestionForm(request.POST or None, request.FILES or None, instance=question)
    if form.is_valid():
        form.author_id = request.user.id
        form.save()
        return redirect(f"question/{question.id}")
    return render(request, "qncy/ask.html", {"form": form} | common_context())
