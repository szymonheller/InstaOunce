from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q, Prefetch
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse

from .forms import UserCreationForm
from .models import Post, User, Comment, Like


class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("photos:feed")
    extra_context = {
        "title": "Rejestracja",
    }

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)


def index(request):
    if request.user.is_authenticated:
        return redirect("photos:feed")
    else:
        context = {}
        return render(request, "photos/index.html", context)


class FeedView(LoginRequiredMixin, ListView):
    template_name = "photos/feed.html"
    # model = Post
    context_object_name = "post_list"
    extra_context = {
        "title": "feed",
    }

    def get_queryset(self):
        return Post.objects.filter(user__in=self.request.user.following.all()).order_by(
            "-created_timestamp"
        )


class PostView(DetailView):
    template_name = "photos/post.html"
    context_object_name = "post"

    def get_queryset(self):
        q = Q(like__user=self.request.user) & Q(like__like=True)

        return (
            Post.objects.select_related("user")
            .annotate(
                like_count=Count("like", filter=Q(like__like=True)),
                liked_by_user=Count("like", filter=q),
            )
            .prefetch_related(
                Prefetch("comment_set", queryset=Comment.objects.select_related("user"))
            )
        )

    def get_context_data(self, **kwargs):
        context = {
            "title": f"{self.object.user}: {self.object.content}",
        }
        return super().get_context_data(**context)


class UserView(DetailView):
    template_name = "photos/user.html"
    context_object_name = "user"
    queryset = User.objects.all().prefetch_related(
        Prefetch("post_set", queryset=Post.objects.select_related("user"))
    )

    def get_context_data(self, **kwargs):
        context = {
            "title": self.object,
        }
        return super().get_context_data(**context)


class SearchView(ListView):
    context_object_name = "users"
    template_name = "photos/search.html"
    extra_context = {
        "title": "Wyszukiwarka",
    }

    def get_queryset(self):
        phrase = self.request.GET.get("q")
        if phrase is None:
            return User.objects.none()
        return User.objects.filter(
            email__icontains=phrase
        )  # rozbuduj za pomocą Q() (przeszukaj: email LUB imię LUB nazwisko)


@login_required
@require_POST
def like(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    like, created = Like.objects.get_or_create(
        user=request.user, post=post, defaults={"like": True},
    )

    if not created:
        like.like = True
        like.save()

        return HttpResponse(status=200)  # OK

    return HttpResponse(status=201)  # Created


@login_required
@require_POST
def dislike(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    like = get_object_or_404(Like, post=post, user=request.user)
    like.like = False
    like.save()
    return HttpResponse(status=200)


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "photos/create_post.html"
    extra_context = {
        "title": "Dodaj wpis",
    }
    fields = [
        "content",
        "image",
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "photos/update_post.html"
    extra_context = {
        "title": "Edytuj wpis",
    }
    fields = [
        "image",
        "content",
    ]

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user or self.request.user.is_superuser


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user or self.request.user.is_superuser


class CreateComment(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = "photos/create_comment.html"
    extra_context = {
        "title": "Dodaj komentarz",
    }
    fields = [
        "content",
    ]

    def get_success_url(self):
        return self.object.post.get_absolute_url()

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "photos/update_comment.html"
    extra_context = {
        "title": "Edytuj komentarz",
    }
    fields = [
        "content",
    ]

    def get_success_url(self):
        return self.object.post.get_absolute_url()

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user or self.request.user.is_superuser


class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        # return reverse("photos:post", args=[self.object.post.pk])
        return self.object.post.get_absolute_url()

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user or self.request.user.is_superuser
