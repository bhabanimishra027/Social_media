from django import forms
from .models import Post, Profile, Story, Reel


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image', 'video']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio']


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'image', 'video', 'is_highlighted']


class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['caption', 'video']