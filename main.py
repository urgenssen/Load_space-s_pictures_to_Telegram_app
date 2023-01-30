import requests
import os
from urllib.parse import unquote, urlsplit
from dotenv import load_dotenv


def load_image(url, path_to_save):

    response = requests.get(url)
    response.raise_for_status()

    with open(path_to_save, 'wb') as file:
        file.write(response.content)

    print(f"Picture from: {url} was loaded successfully!")


def create_new_or_clean_existing_folder(folder, path_to_folder):

    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        path = path_to_folder+folder+"\\"
        for file_name in os.listdir(path):

            file = path + file_name

            if os.path.isfile(file):
                print('Deleting file:', file)
                os.remove(file)


def fetch_spacex_last_launch(launch_id, folder_name_to_save, path_to_folder):

    create_new_or_clean_existing_folder(folder_name_to_save, path_to_folder)

    url_spacex = f"https://api.spacexdata.com/v5/launches/{launch_id}"

    response = requests.get(url_spacex)
    response.raise_for_status()

    urls_spacex_photos = response.json()["links"]["flickr"]["original"]

    for url_number, url in enumerate(urls_spacex_photos):

        filename = f"{path_to_folder}{folder_name_to_save}\
/spacex_{url_number}.jpeg"
        load_image(url, filename)

    print("Download finished")


def get_file_extension_from_url_address(url):

    url_path = unquote(urlsplit(url)[2])
    file_extension = os.path.splitext(os.path.split(url_path)[-1])[-1]

    return file_extension


def get_nasa_pictures(api_key, quantity_of_pictures,
                      folder_name_to_save, path_to_folder):

    create_new_or_clean_existing_folder(folder_name_to_save, path_to_folder)

    nasa_url = "https://api.nasa.gov/planetary/apod"

    payload = {"api_key": f"{api_key}",
               "count": quantity_of_pictures}

    response = requests.get(nasa_url, params=payload)
    response.raise_for_status()

    nasa_urls = [response.json()[i]["hdurl"] for i
                 in range(len(response.json()))
                 if response.json()[i].get("hdurl") is not None]

    while len(set(nasa_urls)) < quantity_of_pictures:

        payload = {"api_key": f"{api_key}",
                   "count": 1}
        response = requests.get(nasa_url, params=payload)
        response.raise_for_status()

        if response.json()[0].get("hdurl") is not None:
            nasa_urls.append(response.json()[0]["hdurl"])
        else:
            continue

    for url_number, url in enumerate(nasa_urls):
        file_extension = get_file_extension_from_url_address(url)
        filename = f"{path_to_folder}{folder_name_to_save}/nasa_apod_\
{url_number}{file_extension}"
        load_image(url, filename)

    print("Download finished")


def get_epic_pictures(api_key, folder_name_to_save, path_to_folder):

    create_new_or_clean_existing_folder(folder_name_to_save, path_to_folder)

    epic_url = "https://api.nasa.gov/EPIC/api/natural/images"
    epic_url_archive = "https://api.nasa.gov/EPIC/archive/natural/"

    payload = {"api_key": f"{api_key}"}

    response = requests.get(epic_url, params=payload)
    response.raise_for_status()

    for item_number, item in enumerate(response.json()):
        epicname = item["image"]+".png"
        date = item["date"].split()[0].replace("-", "/")
        epicfile_url = epic_url_archive+date+"/png/" +\
            epicname+f"?api_key={api_key}"
        filename = f"{path_to_folder}{folder_name_to_save}\
/epic_image_{item_number}.png"
        load_image(epicfile_url, filename)

    print("Download finished")


if __name__ == "__main__":

    load_dotenv()

    user_token = os.environ["NASA_TOKEN"]
    user_path = os.environ["USER_PATH"]
    launch_id = os.environ["LAUNCH_ID"]

    try:
        folder_name_to_save = "Images"
        fetch_spacex_last_launch(launch_id, folder_name_to_save, user_path)
        print(f"Pictures from SpaceX's launch id: {launch_id} \
were download to {user_path}{folder_name_to_save}\n")
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidURL) as error:
        print("Can't get data from server.\nThere is:\n{0}\n"
              .format(error))

    try:
        folder_name_to_save = "NASA_images"
        quantity_of_pictures = 3
        get_nasa_pictures(user_token, quantity_of_pictures,
                          folder_name_to_save, user_path)
        print(f"Random {quantity_of_pictures} NASA's astronomy \
pictures of the day were download to \
{user_path}{folder_name_to_save}\n")
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidURL) as error:
        print("Can't get data from server.\nThere is:\n{0}\n"
              .format(error))

    try:
        folder_name_to_save = "EPIC_images"
        get_epic_pictures(user_token, folder_name_to_save, user_path)
        print(f"Recent EPIC photos were download to \
{user_path}{folder_name_to_save}\n")
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidURL) as error:
        print("Can't get data from server.\nThere is:\n{0}\n"
              .format(error))
