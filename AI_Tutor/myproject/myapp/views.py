from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Max
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Question, Answer, Vote
from .forms import QuestionForm, AnswerForm
from .moderation import moderate_content
import json

# Home Page - Displays all questions with sorting options
def index(request):
    sort_by = request.GET.get('sort', 'newest')
    
    if sort_by == 'most_answered':
        questions = Question.objects.annotate(answer_count=Count('answers')).order_by('-answer_count', '-created_at')
    elif sort_by == 'active':
        questions = Question.objects.annotate(last_answer=Max('answers__created_at')).order_by('-last_answer', '-created_at')
    else:
        questions = Question.objects.order_by('-created_at')

    context = {
        'questions': questions,
        'sort_by': sort_by,
        'total_questions': Question.objects.count(),
        'total_answers': Answer.objects.count(),
        'questions_solved': Question.objects.filter(has_accepted_answer=True).count(),
    }

    return render(request, "myapp/index.html", context)

# Ask a Question (Moderated by Groq API)
@login_required
def ask_question(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        expected_outcome = request.POST.get("expected_outcome")
        full_text = f"{title} {content} {expected_outcome}"

        is_approved = moderate_content(full_text)
        if is_approved != "study-related":
            messages.error(request, "❌ Your question is not study-related. Please review our guidelines.")
            return redirect("ask_question")

        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            messages.success(request, "✅ Your question has been submitted successfully!")
            return redirect("index")
    else:
        form = QuestionForm()
    
    return render(request, "myapp/question.html", {"form": form})

# View Question Details
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question).order_by('-created_at')
    return render(request, "myapp/question_detail.html", {"question": question, "answers": answers, "form": AnswerForm()})

# Answer a Question (Moderated via Groq API, AJAX Submission)
@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "").strip()

        is_approved = moderate_content(content)
        if is_approved != "study-related":
            return JsonResponse({"success": False, "error": "❌ Your answer is not study-related."})

        form = AnswerForm({"content": content})
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            return JsonResponse({
                "success": True,
                "id": answer.id,
                "author": answer.author.username,
                "content": answer.content,
                "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M"),
                "votes": 0
            })
    return JsonResponse({"success": False, "error": "Invalid request method."})

# Vote on an Answer# Ask a Question (Moderated by Groq API)
@login_required
def ask_question(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        expected_outcome = request.POST.get("expected_outcome")
        full_text = f"{title} {content} {expected_outcome}"

        is_approved = moderate_content(full_text)
        if is_approved != "study-related":
            print(f"🚨 Non-study-related question detected: {full_text}")  # Print to terminal
            messages.error(request, "❌ Your question is not study-related. Please review our guidelines.")
            return redirect("ask_question")

        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            messages.success(request, "✅ Your question has been submitted successfully!")
            return redirect("index")
    else:
        form = QuestionForm()
    
    return render(request, "myapp/question.html", {"form": form})

# Answer a Question (Moderated via Groq API, AJAX Submission)
@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "").strip()

        is_approved = moderate_content(content)
        if is_approved != "study-related":
            print(f"🚨 Non-study-related answer detected: {content}")  # Print to terminal
            return JsonResponse({"success": False, "error": "❌ Your answer is not study-related."})

        form = AnswerForm({"content": content})
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            return JsonResponse({
                "success": True,
                "id": answer.id,
                "author": answer.author.username,
                "content": answer.content,
                "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M"),
                "votes": 0
            })
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def vote_answer(request, answer_id, action):
    answer = get_object_or_404(Answer, id=answer_id)
    if action == "upvote":
        answer.votes += 1
    elif action == "downvote":
        answer.votes -= 1
    answer.save()
    return JsonResponse({"votes": answer.votes})

# User Signup
def signup_view(request):
    if request.method == "POST":
        display_name = request.POST.get("display_name").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirm-password").strip()

        if not display_name or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered. Please log in.")
            return redirect("signup")

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect("signup")

        user = User.objects.create_user(username=display_name, email=email, password=password)
        user.save()
        login(request, user)
        messages.success(request, "Signup successful! Welcome to the Q&A Forum.")
        return redirect("index")

    return render(request, "myapp/signup.html")

# User Profile
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    questions = Question.objects.filter(author=user).order_by('-created_at')
    return render(request, "myapp/user_profile.html", {'user_profile': user, 'questions': questions})

# User Login
@login_required
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "myapp/login.html")
