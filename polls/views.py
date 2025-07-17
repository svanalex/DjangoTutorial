from django.db.models import F
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question
from .forms import QuestionForm, ChoiceFormSet
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    
@method_decorator(never_cache, name='dispatch')
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

@login_required
def vote(request, question_id):
    print("user:", request.user)
    print("authenticated:", request.user.is_authenticated)

    question = get_object_or_404(Question, pk=question_id)
    if not question.is_open():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "This poll is not open for voting.",
        })
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing with POST data.
        # This prevents data from being posted twice if a user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    #return HttpResponse(f"You're voting on question {question_id}")

from .forms import QuestionForm, ChoiceFormSet

@login_required
def create_poll(request):
    if request.method == "POST":
        q_form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST, queryset=Choice.objects.none())

        if q_form.is_valid() and formset.is_valid():
            question = q_form.save(commit=False)
            question.creator = request.user
            question.pub_date = timezone.now()
            question.save()

            for form in formset:
                if form.cleaned_data.get('choice_text'):
                    choice = form.save(commit=False)
                    choice.question = question
                    choice.save()

            return redirect('polls:index')
    else:
        q_form = QuestionForm()
        formset = ChoiceFormSet(queryset=Choice.objects.none())

    return render(request, 'polls/create_poll.html', {
        'q_form': q_form,
        'formset': formset
    })


class RegisterView(generic.View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'login/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('polls:index'))
        return render(request, 'login/register.html', {'form': form})
    
class LoginView(generic.View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(reverse('polls:index'))
        return render(request, 'login/login.html', {'form': form})
    
class LogoutView(generic.View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('polls:index'))
    
    def post(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('polls:index'))