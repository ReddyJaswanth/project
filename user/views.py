from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserChat, ChatSession, Document
import pickle
from keras.models import load_model
from django.conf import settings
import os
import random
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

model = load_model("media/models/chatbot_model.h5")

with open("media/models/vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)

with open("media/models/label_encoder.pkl", "rb") as file:
    label_encoder = pickle.load(file)

with open("media/models/tag_responses.pkl", "rb") as file:
    tag_responses = pickle.load(file)

with open("media/models/keyword_documents.json", "r") as file:
    keyword_documents = json.load(file)

def preprocess_text(text):
    return text.lower().strip()

def chatbot_response(user_input):
    user_input_vectorized = vectorizer.transform([user_input]).toarray()
    predicted_tag = label_encoder.inverse_transform(
        [np.argmax(model.predict(user_input_vectorized))]
    )[0]
    response = random.choice(tag_responses[predicted_tag])
    print(response)
    return response


# Create your views here.
@login_required
def userhome(request):
    user = request.user
    return render(request, "user/userhomepage.html", {"user": user})


@login_required
def updateprofile(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        user = request.user

        if username:
            user.username = username
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email

        user.save()
        return redirect("userhome")
    else:
        return redirect("userhome")

@login_required
def userchat(request):
    user = request.user
    sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
    session_id = request.GET.get("session_id")
    chats = []

    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=user)
        chats = UserChat.objects.filter(session=session).order_by("timestamp")

    context = {
        "sessions": sessions,
        "chats": chats,
        "session_id": session_id,
        "username": user.username,
        "email": user.email,
    }
    return render(request, "user/userchat.html", context)

@login_required
def userchat_action(request, session_id=None):
    user = request.user

    if request.method == "POST":
        user_input = preprocess_text(request.POST.get("user_input", "").lower().strip())
        if not user_input:
            return redirect("userchat_action", session_id=session_id)

        document_to_send = None
        description = ""
        matched_keyword = None
        keywords = list(keyword_documents.keys())

        # NLP processing
        vectorizer = TfidfVectorizer().fit_transform([user_input] + keywords)
        vectors = vectorizer.toarray()
        cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

        max_similarity_index = cosine_similarities.argmax()
        if (cosine_similarities[max_similarity_index] > 0.5):  # Adjust the threshold as needed
            matched_keyword = keywords[max_similarity_index]
            document_to_send = keyword_documents[matched_keyword]["file"]
            description = keyword_documents[matched_keyword]["description"]

        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
        else:
            session = ChatSession.objects.create(user=user)

        bot_response = chatbot_response(user_input) if not document_to_send else ""
        chat_entry = UserChat.objects.create(
            session=session, user_input=user_input, result=bot_response
        )

        bot_response_html = bot_response
        console_response = bot_response
        if document_to_send:
            document_path = os.path.join(settings.MEDIA_ROOT, document_to_send)
            if os.path.exists(document_path):
                document_url = os.path.join(settings.MEDIA_URL, document_to_send)
                bot_response =(
                     f"Section {matched_keyword} details:\nDescription: {description}\n\n"
                f'<a href="{document_url}" target="_blank" style="color:blue;">{document_to_send}</a>'
                )
                bot_response_html = bot_response.replace("\n", "<br>")  # For HTML rendering
                console_response = bot_response
                Document.objects.create(chat=chat_entry, file=document_to_send)
            else:
                bot_response = "Sorry, the document could not be found."
                bot_response_html = bot_response
                console_response = bot_response

            chat_entry.result = bot_response_html
            chat_entry.save()

        # Log the response to the console
        print(console_response)

        chats = UserChat.objects.filter(session=session).order_by("timestamp")
        context = {
            "user_message": user_input,
            "results": [bot_response_html],
            "session_id": session.id,
            "chats": chats,
            "sessions": ChatSession.objects.filter(user=user).order_by("-created_at"),
        }
        return render(request, "user/userchat.html", context)
    else:
        sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
            chats = UserChat.objects.filter(session=session).order_by("timestamp")
        else:
            chats = []

        context = {"sessions": sessions, "chats": chats, "session_id": session_id}

        return render(request, "user/userchat.html", context)


@login_required
def delete_chat_session(request, session_id):
    user = request.user
    session = get_object_or_404(ChatSession, id=session_id, user=user)

    if request.method == "POST":
        chats = UserChat.objects.filter(session=session)
        for chat in chats:
            documents = chat.documents.all()
            for document in documents:
                pass  
        session.delete()
        return redirect("userchat")

    context = {"session": session}
    return render(request, "user/userchat.html", context)

@login_required
def previous_chats(request):
    user = request.user
    sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
    context = {"sessions": sessions, "username": user.username, "email": user.email}
    return render(request, "user/previous_chats.html", context)

@login_required
def chat_details(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    chats = UserChat.objects.filter(session=session).order_by("timestamp")
    chat_data = [
        {"user_input": chat.user_input, "result": chat.result} for chat in chats
    ]
    return JsonResponse({"chats": chat_data})

@login_required
def userchat_view(request):
    user_chats = UserChat.objects.filter(user=request.user)
    documents = Document.objects.filter(chat__in=user_chats)
    print(documents)
    context = {
        'sessions': user_chats,
        'documents': documents,
        'username': request.user.username,
        'email': request.user.email,
    }
    return render(request, 'userchat.html', context)