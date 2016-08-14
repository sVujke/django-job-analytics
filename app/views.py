from django.shortcuts import render
from app_modules import mongo_queries
import numpy as np
import pandas as pd
import datetime,pytz

# returns todays date if it has passed 6PM and yesterdays date if not
def yesterday_or_today():
    now = datetime.datetime.now(pytz.timezone("Europe/Belgrade"))
    today_fivepm = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now > today_fivepm:
        #print now.replace(hour=19, minute=0, second=0, microsecond=0)
        return now.replace(hour=19, minute=0, second=0, microsecond=0)
    else:
        #print now.replace(hour=17, minute=0, second=0, microsecond=0)-datetime.timedelta(days=1)
        return now.replace(hour=19, minute=0, second=0, microsecond=0)-datetime.timedelta(days=1)

def ad_numid(query_set):
    item_list = []
    num_id = 0
    for q in query_set:
        subdict = {}
        subdict["name"] = q
        subdict["id"] = num_id
        item_list.append(subdict)
        num_id += 1
    return item_list

def date_to_string(date):
    return date.strftime("%d-%m-%Y")

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
    filtered = []
    for i in collection:
        if value in i["name"].lower():
            filtered.append(i)

    return filtered

def get_stats(x_list):
    df = pd.DataFrame.from_dict(x_list)
    df = df.drop("_id",1)
    dict_describe = df.describe().to_dict()
    stats = dict_describe["count"]

    for key in stats:
        stats[key] = round(stats[key],2)

    key_modificator(x_list)

    stats["q1"] = stats["25%"]
    stats["q2"] = stats["50%"]
    stats["q3"] = stats["75%"]

    return stats


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
        "date": date_to_string(yesterday_or_today())
    }

    return render(request, 'home.html', context)


def list(request, slug):
    query_set = mongo_queries.unique(slug)
    query_set = ad_numid(query_set)
    item_list = query_set
    name = {
        "city": "Cities",
        "position": "Positions",
        "tags": "Tags",
        "firm": "Companies"
    }

    headline_css = slug + "-title"
    div_css = slug + "-div"
    list_css = slug + "-list"

    filter = False

    if request.method == "GET":
        query = request.GET.get("filter")
        if query:
            filtered_set = search(query_set, query.lower())
            filter = True

    if filter == True:
        item_list = filtered_set

    context = {
        "item_list": item_list,
        "num_items": len(item_list),
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


    stats = get_stats(timeline)

    context = {
        "item_name": item_name,
        "timeline": timeline,
        "stats": stats,
        "headline_css": headline_css,
    }

    return render(request, 'item.html', context)

def timeline(request):

    time_line = mongo_queries.timeline_for_all()

    stats = get_stats(time_line)
    context = {
        "timeline": time_line,
        "stats": stats,
        "n_days": int(stats["count"]),
    }

    return render(request, 'timeline.html', context)

def trending(request):

    tags = mongo_queries.unique("tags")[:10]

    cities = mongo_queries.unique("city")[:10]

    positions = mongo_queries.unique("position")[:10]

    firms =mongo_queries.unique("firm")[:10]

    context = {
        "tags":tags,
        "cities":cities,
        "positions": positions,
        "firms": firms,
    }

    return render(request, 'trending.html', context)