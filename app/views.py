from django.shortcuts import render
from app_modules import mongo_queries
import numpy as np
import pandas as pd
import datetime,pytz

# this calculates the z-score
def z_score(last_record, stats):
    if stats["std"] != 0 and np.isnan(stats["std"]) != True:
        return round((last_record - stats["mean"])/ stats["std"],2)
    else:
        return 0

# this calculates z-score for specific key value pair for the last tail_x days
def get_zscore_by_key_val(key,val, tail_x):
    dict_timeline = mongo_queries.timeline_for_key(key,val)
    #print dict_timeline
    df_timeline = pd.DataFrame.from_dict(dict_timeline)
    #print df_timeline
    df_count = df_timeline["count"].tail(tail_x)
    #print df_count
    #print df_count
    stats = {}
    stats["mean"] = df_count.mean()
    stats["std"] = df_count.std()
    #print stats
    last_record = df_count.tail(1)
    last_record = last_record.values[0]
    #print last_record
    return z_score(last_record, stats)

# returns top x trending by key
def get_top_trending_x(key, x, tail_x ):
    rang = []
    query_set = mongo_queries.unique(key)
    for q in query_set:
        sub = []
        sub.append(q)
        sub.append(get_zscore_by_key_val(key,q,tail_x))
        rang.append(sub)
    trending = sorted(rang, key=lambda x: x[1], reverse=True)
    #print trending
    return trending[:x]


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
    #print timeline

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

    tags = get_top_trending_x("tags", 10, 7)

    cities = get_top_trending_x("city", 10, 7)

    positions = get_top_trending_x("position", 10, 7)

    firms = get_top_trending_x("firm", 10, 7)

    context = {
        "tags":tags,
        "cities":cities,
        "positions": positions,
        "firms": firms,
    }

    return render(request, 'trending.html', context)

def compare(request):

    mapper = {
        "Companies": "firm",
        "Positions": "position",
        "Cities": "city",
        "Tags": "tags"
    }

    if request.method == "POST":
        item_1 = request.POST.get("item-1")
        item_2 = request.POST.get("item-2")
        item_3 = request.POST.get("item-3")
        item_4 = request.POST.get("item-4")
        item_5 = request.POST.get("item-5")
        title = request.POST.get("title")

        print item_1, item_2, item_3, item_4, item_5, title

        key = mapper[title]

        items_1 = mongo_queries.timeline_for_key(key, item_1)
        items_2 = mongo_queries.timeline_for_key(key, item_2)
        items_3 = mongo_queries.timeline_for_key(key, item_3)
        items_4 = mongo_queries.timeline_for_key(key, item_4)
        items_5 = mongo_queries.timeline_for_key(key, item_5)

        key_modificator(items_1)
        key_modificator(items_2)
        key_modificator(items_3)
        key_modificator(items_4)
        key_modificator(items_5)

    print len(items_1), len(items_2), len(items_3), len(items_4), len(items_5)

    headline_css = key+"-title"

    context = {
        "items_1": items_1,
        "items_2": items_2,
        "items_3": items_3,
        "items_4": items_4,
        "items_5": items_5,
        "items_1_name": item_1,
        "items_2_name": item_2,
        "items_3_name": item_3,
        "items_4_name": item_4,
        "items_5_name": item_5,
        "headline_css": headline_css,
    }

    return render(request, 'compare.html', context)