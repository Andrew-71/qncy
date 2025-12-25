from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.core.exceptions import PermissionDenied

from qncy.models import Question, Tag, Answer
from qncy.forms import QuestionForm, AnswerForm
from qncy.centrifugo import publish_server

from core.models import User


def paginator_page(request, objects):
    # There's probably a more pythonistic way to do this
    page = 1
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        pass
    page_size = 20
    try:
        page_size = int(request.GET.get("pagesize", 20))
    except ValueError:
        pass
    paginator = Paginator(objects, page_size)
    return paginator.get_page(page)


def index(request):
    latest_questions = Question.objects.get_new()
    page = paginator_page(request, latest_questions)
    if request.user.is_authenticated:
        page.object_list = Question.objects.annotate_votes(
            page.object_list, request.user
        )
    context = {
        "page_obj": page,
    }
    return render(request, "qncy/index.html", context)


def hot(request):
    hot_questions = Question.objects.get_hot()
    page = paginator_page(request, hot_questions)
    if request.user.is_authenticated:
        page.object_list = Question.objects.annotate_votes(
            page.object_list, request.user
        )
    context = {
        "page_obj": page,
    }
    return render(request, "qncy/hot.html", context)


def by_user(request, user_name):
    author = get_object_or_404(User, username=user_name)
    questions = Question.objects.get_by(author)
    page = paginator_page(request, questions)
    if request.user.is_authenticated:
        page.object_list = Question.objects.annotate_votes(
            page.object_list, request.user
        )
    context = {
        "page_obj": page,
        "author": author,
    }
    return render(request, "qncy/profile.html", context)


def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    answers_list = Answer.objects.for_question(question)
    page = paginator_page(request, answers_list)
    if request.user.is_authenticated:
        page.object_list = Answer.objects.annotate_votes(page.object_list, request.user)
    context = {
        "question": question,
        "page_obj": page,
    }

    if request.user.is_authenticated:
        answer = Answer(question=question, author=request.user)
        form = AnswerForm(instance=answer)
        if request.method == "POST":
            form = AnswerForm(request.POST, request.FILES, instance=answer)
            if form.is_valid():
                form.save()
                publish_server(f"questions:{question.id}")
                return HttpResponseRedirect(request.path_info)
        context["form"] = form

    return render(request, "qncy/question.html", context)


def answers(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    answers_list = Answer.objects.for_question(question)
    page = paginator_page(request, answers_list)
    if request.user.is_authenticated:
        page.object_list = Answer.objects.annotate_votes(page.object_list, request.user)
    context = {
        "question": question,
        "page_obj": page,
    }

    return render(request, "qncy/answer_list.html", context)


def tagged(request, tag_name):
    tag_name = tag_name.replace("+", " ")
    tag = get_object_or_404(Tag, name=tag_name)
    tagged_questions = Question.objects.get_tagged(tag)
    page = paginator_page(request, tagged_questions)
    if request.user.is_authenticated:
        page.object_list = Question.objects.annotate_votes(
            page.object_list, request.user
        )
    context = {
        "tag": tag,
        "page_obj": page,
    }
    return render(request, "qncy/tagged.html", context)


@login_required
def ask(request):
    question = Question(author=request.user)
    form = QuestionForm(instance=question)
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            form.save()
            return redirect("qncy:question", question_id=question.id)
    return render(request, "qncy/ask.html", {"form": form})


@require_POST
@login_required
def vote_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exists = False
    up = True
    if request.POST.get("clear") is not None:
        question.clear_vote(request.user)
    elif request.POST.get("up") is not None:
        question.vote(request.user, True)
        exists = True
    elif request.POST.get("down") is not None:
        question.vote(request.user, False)
        exists = True
        up = False
    else:
        return HttpResponseBadRequest("Type of vote not specified.")
    context = {"submission": question, "exists": exists, "up": up}
    html = render_to_string("qncy/voting.html", context, request=request)
    return HttpResponse(html)


@require_POST
@login_required
def vote_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    exists = False
    up = True
    if request.POST.get("clear") is not None:
        answer.clear_vote(request.user)
    elif request.POST.get("up") is not None:
        answer.vote(request.user, True)
        exists = True
    elif request.POST.get("down") is not None:
        answer.vote(request.user, False)
        exists = True
        up = False
    else:
        return HttpResponseBadRequest("Type of vote not specified.")

    context = {"submission": answer, "exists": exists, "up": up}
    html = render_to_string("qncy/voting.html", context, request=request)
    publish_server(f"questions:{answer.question.id}")
    return HttpResponse(html)


@require_POST
@login_required
def accept_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if request.user != answer.question.author:
        raise PermissionDenied("Only question owner can accept answers.")
    if request.POST.get("clear") is not None:
        answer.clear_accept()
    elif request.POST.get("accept") is not None:
        answer.accept()
    else:
        return HttpResponseBadRequest("Type of acceptance not specified.")

    answers_list = Answer.objects.for_question(answer.question)
    page = paginator_page(request, answers_list)
    page.object_list = Answer.objects.annotate_votes(page.object_list, request.user)
    context = {
        "page_obj": page,
        "question": answer.question,
    }
    html = render_to_string("qncy/answer_list.html", context, request=request)
    publish_server(f"questions:{answer.question.id}")
    return HttpResponse(html)


@require_POST
def search(request):
    query = request.POST.get("q", "")
    if query:
        results = Question.objects.search(query)
    else:
        results = Question.objects.none()
    page = paginator_page(request, results)
    context = {
        "page_obj": page,
        "query": query,
    }
    return render(request, "qncy/search_results.html", context)
