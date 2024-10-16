from django.shortcuts import render,redirect
from . import util
import markdown2
import random
from django import forms

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

##Entry
def entry(request, title):
    content = util.get_entry(title)
    if content == None:
        return render(request, "encyclopedia/error.html", {"message": "Entry not found. Please try again"})
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(content)
    })

##Search function
def search(request):
    query = request.GET.get("q", "")
    if util.get_entry(query):
        return redirect("entry", title=query)
    else:
        results = [entry for entry in util.list_entries() if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "results": results,
            "query": query
        })
    
##To create a new page
class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")

def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # Check if an entry with the title already exists
            if util.get_entry(title):
                return render(request, "encyclopedia/error.html", {
                    "message": "An entry with this title already exists."
                })
            full_content = f"# {title}\n\n{content}"
            util.save_entry(title, full_content)
            return redirect("entry", title=title)
    else:
        form = NewEntryForm()
    return render(request, "encyclopedia/create.html", {"form": form})

##Edit
def edit(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {"message": "Entry not found."})

    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            #new_title = form.cleaned_data["title"]
            new_content = form.cleaned_data["content"]
            util.save_entry(title, new_content)
            return redirect("entry", title=title)
    else:
        form = NewEntryForm(initial={"title": title, "content": content})
    return render(request, "encyclopedia/edit.html", {"form": form, "title": title, "content": content})
    
def save_edit(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        # Debugging
        print(f"Received title: {title}")
        print(f"Received content: {content}")
        if title and content.strip():
            util.save_entry(title, content)
            return redirect("entry", title=title)
        else:
            return render(request, "encyclopedia/error.html", {"message": "Title and content cannot be empty."})
    return redirect("index")
 
##Random pages
def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect("entry", title=random_entry)