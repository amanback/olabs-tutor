from django.urls import path
from .views import (
    index, ask_question, question_detail, vote_answer, 
    signup_view, login_view, user_profile, answer_question, moderate_content
)

urlpatterns = [
    path("", index, name="index"),
    path("ask/", ask_question, name="ask_question"),
    path("question/<int:question_id>/", question_detail, name="question_detail"),
    path("question/<int:answer_id>/vote/", vote_answer, name="vote_answer"),  # ✅ Fixed conflict
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("user/<int:user_id>/", user_profile, name="user_profile"),
    path("answer-question/<int:question_id>/", answer_question, name="answer_question"),
    path("moderate-content/", moderate_content, name="moderate_content"),
]
