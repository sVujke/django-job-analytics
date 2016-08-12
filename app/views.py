from django.shortcuts import render
from app_modules import mongo_queries
import numpy as np
import pandas as pd
import datetime

# returns todays date if it has passed 6PM and yesterdays date if not
def yesterday_or_today():
    now = datetime.datetime.utcnow()
    today_fivepm = now.replace(hour=17, minute=0, second=0, microsecond=0)
    if now > today_fivepm:
        return now.replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        return now.replace(hour=16, minute=0, second=0, microsecond=0)-datetime.timedelta(days=1)

def get_current_datetime():
    now = datetime.datetime.utcnow()
    return now.replace(hour=16, minute=0, second=0, microsecond=0)

def make_slug(word):
    if " " not in word:
        return word.lower()
    word = word.replace("/", "@").replace(" ", "#")
    return word


def r_slug(slug):
    if len(slug) == 1:
        return slug.capitalize()
    word = slug.replace("/", "@").replace(" ", "#")
    return word


def key_modificator(x_list):
    for i in x_list:
        i["id"] = i["_id"]


def search(collection, value):
    subset = []
    for i in collection:
        if value in i.lower():
            subset.append(i)

    return subset


# Create your views here.
def home(request):
    add_num = mongo_queries.count_by_key("date", yesterday_or_today())
    top_tags = mongo_queries.top_x(10, "date", yesterday_or_today(), "$tags")
    top_cities = mongo_queries.top_x(5, "date", yesterday_or_today(), "$city")
    top_firms = mongo_queries.top_x(10, "date", yesterday_or_today(), "$firm")
    top_positions = mongo_queries.top_x(10, "date", yesterday_or_today(), "$position")

    key_modificator(top_tags)
    key_modificator(top_cities)
    key_modificator(top_positions)
    key_modificator(top_firms)

    context = {
        "test": "Test",
        "add_num": add_num,
        "top_tags": top_tags,
        "top_cities": top_cities,
        "top_firms": top_firms,
        "top_positions": top_positions,
    }

    return render(request, 'home.html', context)


# def tags(request):
#
#     tags = mongo_queries.unique("tags")
#
#     if request.method == "GET":
#         query = request.GET.get("filter")
#         if query:
#             tags = search(tags,query)
#
#     context = {
#         "tags": tags,
#     }
#
#     return render(request, 'tags.html', context)

def list(request, slug):
    query_set = mongo_queries.unique(slug)

    name = {
        "city": "Cities",
        "position": "Positions",
        "tags": "Tags",
        "firm": "Companies"
    }

    headline_css = slug + "-title"
    div_css = slug + "-div"
    list_css = slug + "-list"

    if request.method == "GET":
        query = request.GET.get("filter")
        if query:
            query_set = search(query_set, query.lower())

    item_list = []
    num_id = 0
    for q in query_set:
        subdict = {}
        subdict["name"] = q
        subdict["id"] = num_id
        item_list.append(subdict)
        num_id = num_id + 1

    context = {
        "item_list": item_list,
        "title": name[slug],
        "headline_css": headline_css,
        "div_css": div_css,
        "list_css": list_css,
        "slug": slug,
    }

    return render(request, 'list.html', context)


def item(request, slug, id):

    headline_css = slug + "-title"
    query_set = mongo_queries.unique(slug)

    item_list = []
    num_id = 0
    for q in query_set:
        subdict = {}
        subdict["name"] = q
        subdict["num_id"] = num_id
        item_list.append(subdict)
        num_id = num_id + 1

    item_name = ""
    for i in item_list:
        if i["num_id"] == int(id):
            item_name = i["name"]
            break

    timeline = mongo_queries.timeline_for_key(slug,item_name)

    df = pd.DataFrame.from_dict(timeline)
    df = df.drop("_id",1)
    dict_describe = df.describe().to_dict()
    stats = dict_describe["count"]

    for key in stats:
        stats[key] = round(stats[key],2)

    key_modificator(timeline)

    stats["q1"] = stats["25%"]
    stats["q2"] = stats["50%"]
    stats["q3"] = stats["75%"]
    context = {
        "item_name": item_name,
        "timeline": timeline,
        "stats": stats,
        "headline_css": headline_css,
    }

    return render(request, 'item.html', context)
