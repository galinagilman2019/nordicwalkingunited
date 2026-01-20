
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment
# blog/forms.py


# blog/forms.py
class CommentForm(forms.ModelForm):
    hp = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot

    class Meta:
        model = Comment
        fields = ["name", "email", "body", "images"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
            "images": CKEditor5Widget(config_name="comment"),
        }

    def clean(self):
        cleaned = super().clean()

        # simple honeypot: if filled, treat as spam
        if cleaned.get("hp"):
            raise forms.ValidationError("Spam detected.")

        return cleaned


"""
class CommentForm(forms.ModelForm):
    hp = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot

    class Meta:
        model = Comment
        fields = ["name", "email", "body", "images"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
            "images": CKEditor5Widget(config_name="comment"),
        }

    def clean(self):
        cleaned = super().clean()

        # simple honeypot: if filled, treat as spam
        if cleaned.get("hp"):
            raise forms.ValidationError("Spam detected.")

        return cleaned






class CommentForm(forms.ModelForm):
    # honeypot field you reference as {{ form.hp }}
    hp = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]
        widgets = {
            "body": CKEditor5Widget(config_name="comment"),
        }

    def clean(self):
        cleaned = super().clean()
        # if honeypot filled -> spam
        if cleaned.get("hp"):
            raise forms.ValidationError("Spam detected.")
        return cleaned




class CommentForm(forms.ModelForm):
    hp = forms.CharField(required=False, widget=forms.HiddenInput)  # your honeypot

    class Meta:
        model = Comment
        fields = ["name", "email", "body", "images"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
            "images": CKEditor5Widget(config_name="comment"),
        }

    def clean(self):
        cleaned = super().clean()
        # simple honeypot: if filled, treat as spam
        if cleaned.get("hp"):
            raise forms.ValidationError("Spam detected.")
        return cleaned


from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    # simple honeypot (spam trap); NOT saved to DB
    hp = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]
        labels = {
            "name": "Your name",
            "email": "Email (optional)",
            "body": "Comment",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Jane Doe"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "jane@example.com"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Write your comment…"}),
        }

    def clean(self):
        cleaned = super().clean()
        # If honeypot has content, treat as spam
        if cleaned.get("hp"):
            raise forms.ValidationError("Spam detected.")
        return cleaned
"""
