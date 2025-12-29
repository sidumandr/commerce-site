from django import forms
from .models import Listing, Bid, Comment

class ListingForm(forms.ModelForm):
    price = forms.DecimalField(
        label='Starting Price',
        min_value=0.01,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'imageUrl', 'category']
        labels = {
            'title': 'Title',
            'description': 'Description',
            'imageUrl': 'Image URL (Not Requirement)',
            'category': 'Category (Not Requirement)'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class BidForm(forms.ModelForm):
    bid = forms.DecimalField(
        label='Bid Amount',
        min_value=0.01,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Bid
        fields = ['bid']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']
        labels = {
            'message': 'Your comment',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'}),
        }

