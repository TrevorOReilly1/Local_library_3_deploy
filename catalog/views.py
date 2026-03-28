from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .forms import LoanBookForm
import datetime


from .models import Book, Author, BookInstance, Genre
from .forms import LoanBookForm

import datetime


# -------------------------
# HOME PAGE
# -------------------------

def index(request):
    """View function for home page of site."""
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    return render(request, 'catalog/index.html', context=context)


# -------------------------
# BOOK & AUTHOR LIST/DETAIL
# -------------------------

class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    template_name = 'catalog/author_list.html'


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'


# -------------------------
# USER LOANED BOOKS
# -------------------------

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """List books on loan to the current user."""
    model = BookInstance
    template_name = 'catalog/my_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user,
            status__exact='o'
        ).order_by('due_back')


# -------------------------
# AUTHOR CREATE / UPDATE / DELETE
# -------------------------

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('author_list'))


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('author_list'))


def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    try:
        author.delete()
        messages.success(request, f"{author.first_name} {author.last_name} has been deleted")
    except:
        messages.error(request, f"{author.first_name} {author.last_name} cannot be deleted. Books exist for this author.")
    return redirect('author_list')


# -------------------------
# AVAILABLE BOOKS LIST
# -------------------------

class AvailBooksListView(generic.ListView):
    """List all available books."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_available.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            status__exact='a'
        ).order_by('book__title')


# -------------------------
# LIBRARIAN LOAN VIEW
# -------------------------

@login_required
def loan_book_librarian(request, pk):
    """View for librarian to loan a book instance."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = LoanBookForm(request.POST, instance=book_instance)

        if form.is_valid():
            book_instance = form.save()
            book_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=4)
            book_instance.status = 'o'
            book_instance.save()

            return HttpResponseRedirect(reverse('all_available'))

    else:
        form = LoanBookForm(
            instance=book_instance,
            initial={'book_title': book_instance.book.title}
        )

    return render(request, 'catalog/loan_book_librarian.html', {'form': form})


# -------------------------
# BOOK CREATE / UPDATE / DELETE
# -------------------------

class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()

        # Add selected genres
        for genre in form.cleaned_data['genre']:
            theGenre = get_object_or_404(Genre, name=genre)
            post.genre.add(theGenre)

        post.save()
        return HttpResponseRedirect(reverse('book_list'))


class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']

    def form_valid(self, form):
        post = form.save(commit=False)

        # Remove old genres
        for genre in post.genre.all():
            post.genre.remove(genre)

        # Add new genres
        for genre in form.cleaned_data['genre']:
            theGenre = get_object_or_404(Genre, name=genre)
            post.genre.add(theGenre)

        post.save()
        return HttpResponseRedirect(reverse('book_list'))


class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = '/catalog/books/'
