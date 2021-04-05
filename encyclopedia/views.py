import random
from random import choice
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django import forms
from markdown2 import Markdown
markdowner = Markdown()

from . import util


class SearchForm(forms.Form):
	title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Search...'}), label='')

class NewForm(forms.Form):
    new_title = forms.CharField(label='')
    textarea = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Use Markdown here...'}), label='')

class EditForm(forms.Form):
    textarea = forms.CharField(widget=forms.Textarea(), label='')

# https://docs.djangoproject.com/en/3.0/ref/forms/fields/
def index(request):
    entries = util.list_entries()
    checked = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if title in entries:
                search = util.get_entry(title)
                entry = markdowner.convert(search)
                return render(request, "encyclopedia/wiki.html", {
                    "entry": entry, 
                    "title": title, 
                    "form": SearchForm()
                })
            else:
                for i in entries:
                    if title.lower() in i.lower():
                        checked.append(i)
                return render(request, "encyclopedia/results.html", {
                    "checked": checked, 
                    "form": SearchForm()
                })
        else:
            return render(request, "encyclopedia/index.html", {"form": form})
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(), "form":SearchForm()
        })

def wiki(request, title):
    entry = util.get_entry(title)
    msg = "Your requested page was not found, please try again :)"
    if entry:
        return render(request, "encyclopedia/wiki.html", {
           "title": title, "entry": Markdown().convert(entry),
           "form": SearchForm()
        })
    else:
        return render(request, "encyclopedia/error.html",{
            "msg": msg,
            "form": SearchForm()
        })

def random(request):
    title = choice(util.list_entries())
    return HttpResponseRedirect(reverse('wiki', args=[title]))

def new(request):
    if request.method == "POST":
        entries = util.list_entries()
        form = NewForm(request.POST or None)
        if form.is_valid():
            title = form.cleaned_data["new_title"]
            textarea = form.cleaned_data["textarea"]
            if title in entries:
                return render(request, "encyclopedia/error.html", {
                    "msg": "This entry is already in use.", 
                    "form": SearchForm()
                })
            else:
                util.save_entry(title, textarea)
                return HttpResponseRedirect(reverse('wiki', args=[title]))
    else:
        return render(request, "encyclopedia/new.html", {
            "form": SearchForm(), "create": NewForm()
        })

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            textarea = form.cleaned_data["textarea"]
            util.save_entry(title, textarea)
            return HttpResponseRedirect(reverse('wiki', args=[title]))
        else:
            return render(request, "encyclopedia/edit.html", {"form": form})
    else:
        value = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(), 
            "edit": EditForm(initial={'textarea': value}), 'title': title})

