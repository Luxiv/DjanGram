from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView
from .models import UserAccount, Article, Images
from .forms import NewPostForm, RegistrationUserForm, FullProfileInfoForm
from .utils import DataMixin, send_email_for_verify
from taggit.models import Tag


class Timeline(DataMixin, ListView):
    paginate_by = 3
    model = Article
    template_name = 'main/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Images.objects.all()
        c_def = self.get_user_context(title='DjanGramm')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Article.objects.filter(is_published=True)


class Profile(DataMixin, ListView):
    model = UserAccount
    template_name = 'main/profile.html'
    context_object_name = 'user_info'

    def get_queryset(self):
        u = UserAccount.objects.get(slug=self.kwargs['usr_slug'])
        print(u)
        return u

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Images.objects.all()
        c_def = self.get_user_context(title='Profile',
                                      posts=Article.objects.filter(creator__slug=self.kwargs['usr_slug']))
        return dict(list(context.items()) + list(c_def.items()))


class ViewArticle(DataMixin, DetailView):
    model = Article
    template_name = 'main/article.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        stuff = get_object_or_404(Article, slug=self.kwargs[self.slug_url_kwarg])
        total_likes = stuff.total_likes()
        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True

        context = super().get_context_data(**kwargs)
        context['liked'] = liked
        context['total_likes'] = total_likes
        # context['photos'] = Images.objects.filter(article=) Article.objects.get(slug=self.kwargs[self.slug_url_kwarg])
        c_def = self.get_user_context(title='Article',
                                      photos=Images.objects.filter(article__slug=self.kwargs['post_slug']))
        return dict(list(context.items()) + list(c_def.items()))


def like_view(request, slug):
    post = get_object_or_404(Article, slug=request.POST.get('post_slug'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user.pk)
        liked = True
    return HttpResponseRedirect(reverse('post_view', args=[slug]))


def new_article(request):
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            new_articcle = form.save(commit=False)
            new_articcle.creator = UserAccount.objects.get(username=request.user.username)
            new_articcle.save()
            form.save_m2m()
            for image in images:
                photo = Images(article=new_articcle, image=image)
                photo.save()

            # new_articcle.title_photo = request.FILES.getlist("images")

            return redirect('timeline')
    else:
        form = NewPostForm()
    return render(request, 'main/addpage.html', {'form': form, 'context': 'Add Page'})


# class AddPostImagesView(TemplateView):
#     template_name = "main/add_images.html"
#
#     def post(self, request, *args, **kwargs):
#         try:
#             images = request.FILES.getlist('images')
#             article = Article.objects.get(id=self.kwargs['pk'])
#             for image in images:
#                 article_images = Images(
#                     article=article,
#                     image=image
#                 )
#                 article_images.save()
#             return redirect('timeline')
#         except Exception as e:
#             print(e)


def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)

    #  Filter posts by tag name
    posts = Article.objects.filter(tags=tag)
    context = {
        'tag': tag,
        'posts': posts
    }
    return render(request, 'main/index.html', context)


class RegistrationUser(DataMixin, CreateView):
    form_class = RegistrationUserForm
    template_name = 'main/registration.html'
    success_url = reverse_lazy('timeline')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Registration')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        form.save()
        user = authenticate(username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password1'),
                            email=form.cleaned_data.get('email')
                            )
        # send_email_for_verify(self.request, user)
        login(self.request, user)
        return redirect('add_info')


class FullProfileInfo(DataMixin, UpdateView):
    form_class = FullProfileInfoForm
    model = UserAccount
    slug_url_kwarg = 'usr_slug'
    template_name = 'main/full_profile_info.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Profile Info')
        return dict(list(context.items()) + list(c_def.items()))


class EmailVerify(View):

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and default_token_generator.check_token(user, token):
            user.email_verify = True
            login(request, user)
            return redirect('profile', )
        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            usr = get_user_model()
            uid = urlsafe_base64_decode(uidb64).decode()
            user = usr.default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None
            return user


class LoginUser(DataMixin, LoginView):
    form_class = AuthenticationForm
    template_name = 'main/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Authentication')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('timeline')


def logout_user(request):
    logout(request)
    return redirect('login')


def friends(request):
    user = UserAccount.objects.filter(useraccount__slug=request.user)
    return render(request, 'main/friends.html', {'friends': user, 'context': 'My friends'})


def recommendations(request):
    users = UserAccount.objects.exclude(username=request.user.username)
    if request.method == 'POST':
        user = UserAccount.objects.get(username=request.user.username)
        user.friends.add(UserAccount.objects.get(username=request.POST.get('to_friend')))
    return render(request, 'main/recommendations.html', {'users': users, 'context': 'Recommendations'})


def about(request):
    return render(request, 'main/index.html', {'title': 'Main BlackGramm '})

# class UserFriends(DataMixin, ListView):
#     template_name = 'main/friends.html'
#
#     def get_queryset(self):
#         return UserAccount.objects.all()
# #
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title='Authentication')
#         return dict(list(context.items()) + list(c_def.items()))





def add_page(request):
    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            try:
                Article.objects.create(**form.cleaned_data)
                return redirect('timeline')
            except:
                form.add_error(None, 'Adding post error')
    else:
        form = NewPostForm()
    return render(request, 'main/addpage.html', {'form': form, 'context': 'Add Page'})




# def index(request):
#     posts = Article.objects.all()
#     context = {'menu': menu,
#                'title': 'Main BlackGramm ',
#                'posts': posts}
#     return render(request, 'main/index.html', context=context)

# def profile(request, usr_slug):
#     user = User.objects.get(login=usr_slug)
#     posts = Article.objects.filter(creator=user)
#     context = {'menu': menu,
#                'title': 'Main BlackGramm ',
#                'user_info': user,
#                'posts': posts}
#     return render(request, 'main/profile.html', context=context)

# def view_post(request, post_slug):
#     post = Article.objects.filter(login=post_slug)
#     context = {'menu': menu,
#                'title': 'BlackGramm ',
#                'posts': post}
#     return render(request, 'main/article.html', context=context)


# def new_article(request):
#     if request.method == 'POST':
#         # a = Article()
#         form = NewPostForm(request.POST)  # , instance=a)
#         if form.is_valid():
#             # form.cleaned_data['Author'] = UserAccount.objects.get(username=request.user.username)
#             # try:
#             # author = UserAccount.objects.get(username=request.user.username)
#             new_article_ = Article.objects.create(title=form['title'],
#                                    content=form['content'],
#                                    photo=form['photo'],
#                                    is_published=form['is_published'],
#                                    creator=author
#                                    )
#             print(form)
#             # print(new_article_)
#             # new_article_.save()
#             new_article_ = form.save()
#             # new_article_.creator.add(str(request.user.pk))
#             # new_article_.save()
#             return redirect('timeline')
#             # except:
#             #     form.add_error(None, 'Adding post error')
#     else:
#         form = NewPostForm()
#     return render(request, 'main/addpage.html', {'form': form, 'context': 'Add Page'})

# class NewArticle(LoginRequiredMixin, DataMixin, CreateView):
#     form_class = NewPostForm
#     template_name = 'main/addpage.html'
#     success_url = reverse_lazy('timeline')
#     login_url = reverse_lazy('registration')
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title='New Post')
#         return dict(list(context.items()) + list(c_def.items()))