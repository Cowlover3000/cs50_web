import random
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from markdown2 import markdown
from . import util

from django import forms

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry = util.get_entry(title)
    print("entry")
    if entry is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown(entry),
            "title":title
        })
    else:
        return render(request, "encyclopedia/error.html", {
        "title":title
    })

def error(request, title):
    return

def search(request):
    query = request.GET.get('q')
    entry_list = util.list_entries()
    sub_list = []
    entry = util.get_entry(query)
    if entry is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown(entry),
            "title":query
        })
    
    for item in entry_list:
        if query in item:
            sub_list.append(item)
    
    if sub_list:
        return render(request, "encyclopedia/search.html", {
            "entrys":sub_list
        })  
      
    return render(request, "encyclopedia/error.html", {
        "title":query
    })

def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title):
                # Entry already exists
                return render(request, "encyclopedia/new_page.html", {
                    "form": form,
                    "error": f"The page '{title}' already exists."
                })
            else:
                # Create new entry
                util.save_entry(title, content)
                return redirect("entry", title=title)
    else:
        form = NewPageForm()
        return render(request, "encyclopedia/new_page.html", {
            "form": form
        })

def edit(request, title):
    entry = util.get_entry(title)
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            new_entry = form.cleaned_data["content"]
            util.save_entry(title, new_entry)
            return HttpResponseRedirect(reverse("entry", args=[title]))
    else:
        form = EditForm(initial={"content": entry})
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "title": title
        })


def random_page(request):
    # Get a list of all entries
    entries = util.list_entries()
    
    # Choose a random entry from the list
    random_entry = random.choice(entries)
    
    # Redirect the user to the entry's page
    return redirect('entry', title=random_entry)