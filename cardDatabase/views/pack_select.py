from django.shortcuts import render
from fowsim import constants as CONS


def get(request):
    mapped_clusters = []

    for cluster in CONS.SET_DATA["clusters"]:
        setsData = []
        for fow_set in cluster["sets"]:
            for config in CONS.PACK_OPENING_SETS:
                config += ".json"
                lowerCode = fow_set["code"].lower()
                if config.startswith(lowerCode):
                    setsData.append(
                        {
                            "name": fow_set["name"],
                            "code": fow_set["code"],
                            "image": get_image_for_config(lowerCode),
                        }
                    )
        mapped_clusters.append({"name": cluster["name"], "sets": setsData})

    ctx = {"clusters": mapped_clusters}
    return render(request, "cardDatabase/html/pack_select.html", ctx)


def get_image_for_config(set):
    return "img/pack/" + set + "-pack.png"
