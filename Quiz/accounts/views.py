from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Quiz, Question, Result


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa




from .models import Profile, Quiz, Question, Result




def home(request):
    return render(request, "accounts/home.html")


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # make sure profile exists
            profile, _ = Profile.objects.get_or_create(user=user)

            # Redirect based on role
            if profile.role == "teacher":
                return redirect("teacher_dashboard")
            elif profile.role == "student":
                return redirect("student_dashboard")
            else:
                return redirect("choose_role")  # role not set yet

        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "accounts/login.html")


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # auto-login and go choose role
        login(request, user)
        return redirect('choose_role')

    return render(request, "accounts/register.html")


def user_logout(request):
    logout(request)
    return redirect('login')


def choose_role(request):
    if request.method == "POST":
        role = request.POST.get("role")

        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.role = role
        profile.save()

        if role == "teacher":
            return redirect("teacher_dashboard")
        else:
            return redirect("student_dashboard")

    return render(request, "accounts/choose_role.html")


def teacher_dashboard(request):
    return render(request, "accounts/teacher_dashboard.html")


def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html")



def create_quiz(request):
    if request.method == "POST":
        title = request.POST.get("title")
        time_limit = request.POST.get("time_limit")   # <-- new field

        # Create quiz with time limit
        quiz = Quiz.objects.create(
            teacher=request.user,
            title=title,
            time_limit_minutes=int(time_limit)   # <-- save time limit
        )

        return render(request, "accounts/quiz_created.html", {"quiz": quiz})

    return render(request, "accounts/create_quiz.html")





def add_question(request, quiz_code):
    quiz = Quiz.objects.get(code=quiz_code)

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        option_a = request.POST.get("option_a")
        option_b = request.POST.get("option_b")
        option_c = request.POST.get("option_c")
        option_d = request.POST.get("option_d")
        correct_option = request.POST.get("correct_option")

        Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option
        )

        messages.success(request, "Question added successfully!")
        return redirect("add_question", quiz_code=quiz.code)

    return render(request, "accounts/add_question.html", {"quiz": quiz})


def view_quizzes(request):
    quizzes = Quiz.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, "accounts/view_quizzes.html", {"quizzes": quizzes})





def quiz_results(request, quiz_code):
    quiz = Quiz.objects.get(code=quiz_code)
    results = Result.objects.filter(quiz=quiz)

    context = {
        "quiz": quiz,
        "results": results,
        "total_attempts": results.count()
    }
    return render(request, "accounts/quiz_results.html", context)



def enter_quiz_code(request):
    if request.method == "POST":
        code = request.POST.get("quiz_code").upper()

        try:
            quiz = Quiz.objects.get(code=code)
            return redirect("attempt_quiz", quiz_code=quiz.code)
        except:
            messages.error(request, "Invalid Quiz Code")

    return render(request, "accounts/enter_quiz_code.html")


def attempt_quiz(request, quiz_code):
    quiz = Quiz.objects.get(code=quiz_code)
    questions = quiz.questions.all()

    time_limit = quiz.time_limit_minutes * 60


    if request.method == "POST":
        score = 0
        total = len(questions)

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected == q.correct_option:
                score += 1

        Result.objects.create(
            quiz=quiz,
            student=request.user,
            score=score,
            total=total
        )

        return redirect("student_dashboard")

    return render(request, "accounts/attempt_quiz.html", {
        "quiz": quiz,
        "questions": questions,
        "time_limit": time_limit
    })



def view_attempted_quizzes(request):
    results = Result.objects.filter(student=request.user).order_by('-submitted_at')
    return render(request, "accounts/attempt_history.html", {"results": results})









def download_quiz_results_pdf(request, quiz_code):
    quiz = Quiz.objects.get(code=quiz_code)
    results = Result.objects.filter(quiz=quiz)

    template = get_template("accounts/quiz_results_pdf.html")
    html = template.render({"quiz": quiz, "results": results})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}_results.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF")

    return response


