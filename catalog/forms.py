from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Book, BookInstance


class LoanBookForm(forms.ModelForm):
    """Form for a librarian to loan books."""
    book_title = forms.CharField(disabled=True, required=False)

    class Meta:
        model = BookInstance
        fields = ('book_title', 'borrower')


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre', 'book_image']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
