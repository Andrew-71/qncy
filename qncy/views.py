from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from qncy.models import Question, Tag, Answer
from qncy.forms import QuestionForm, AnswerForm

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

def index(request):
    latest_questions = Question.objects.get_new()
    context = {
        "page_obj": paginator_page(request, latest_questions),
    }
    return render(request, "qncy/index.html", context)

def hot(request):
    hot_questions = Question.objects.get_hot()
    context = {
        "page_obj": paginator_page(request, hot_questions),
    }
    return render(request, "qncy/hot.html", context)

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    answers_list = Answer.objects.for_question(question)
    context = {
        "question": question,
        "page_obj": paginator_page(request, answers_list),
    }
    
    if request.user.is_authenticated:
        answer = Answer(question=question,author=request.user)
        form = AnswerForm(request.POST or None, request.FILES or None, instance=answer)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
        context['form'] = form

    return render(request, "qncy/question.html", context)

def tagged(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    tagged_questions = Question.objects.get_tagged(tag)
    context = {
        "tag": tag,
        "page_obj": paginator_page(request, tagged_questions),
    }
    return render(request, "qncy/tagged.html", context)

@login_required
def ask(request):
    question = Question(author=request.user)
    form = QuestionForm(request.POST or None, request.FILES or None, instance=question)
    if form.is_valid():
        form.save()
        return redirect("qncy:question", question_id=question.id)
    return render(request, "qncy/ask.html", {"form": form})

@login_required
def vote_question(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        up = True
        if request.POST.get("up") is not None:
            up = True
        elif request.POST.get("down") is not None:
            up = False
        else:
            return HttpResponseBadRequest()
        question.vote(request.user, up)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    return redirect("qncy:index")

@login_required
def vote_answer(request, answer_id):
    if request.method == 'POST':
        next = request.POST.get('next', '/')
        answer = get_object_or_404(Answer, id=answer_id)
        if request.POST.get("accept") is not None:
            if request.user != answer.question.author:
                raise PermissionDenied()
            answer.accept(request.user)
            return HttpResponseRedirect(next)
        up = True
        if request.POST.get("up") is not None:
            up = True
        elif request.POST.get("down") is not None:
            up = False
        else:
            return HttpResponseBadRequest()
        answer.vote(request.user, up)
        return HttpResponseRedirect(next)
    return redirect("qncy:index")
