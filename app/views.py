from django.shortcuts import render
from app_modules import mongo_queries


def key_modificator(x_list):
    for i in x_list:
        i["id"] = i["_id"]
# Create your views here.
def home(request):

    add_num = mongo_queries.count_by_key("date","29/07/16")
    top_tags = mongo_queries.top_x(10,"date","29/07/16","$tags")
    top_cities = mongo_queries.top_x(5,"date","29/07/16","$city")
    top_firms = mongo_queries.top_x(10,"date","29/07/16","$firm")
    top_positions = mongo_queries.top_x(10,"date","29/07/16","$positions")

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