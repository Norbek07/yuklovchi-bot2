import requests

def get_insta(link):
    url = "https://instagram-downloader.p.rapidapi.com/index"

    querystring = {"url":link}

    headers = {
        "X-RapidAPI-Key": "e09cc2700bmshb93f24e11f7c72fp174b47jsn0eaef815fac4",
        "X-RapidAPI-Host": "instagram-downloader.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    result = response.json()
    return result