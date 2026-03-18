import requests
import json
import os 
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')  # Load environment variables from .env file

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxresults = 50
def get_channel_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        data = response.json()
        # print(json.dumps(data, indent=4))
        channel_items = data["items"][0]
        channel_playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        return channel_playlist_id
        # print(channel_playlist_id)
    except requests.exceptions.RequestException as e:
        raise e


def get_video_ids(playlist_id):
    video_ids = []
    page_token = None
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxresults}&playlistId={playlist_id}&key={API_KEY}"
    try:
        while True:
            url = base_url
            if page_token:
                url += f"&pageToken={page_token}"        
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)
            page_token = data.get("nextPageToken")
            if not page_token:
                break
            return video_ids
    except requests.exceptions.RequestException as e:
        raise e

def extract_video_data(video_id_lst):
    video_details = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id:video_id + batch_size]
    try:
        for batch in batch_list(video_id_lst, maxresults):
            video_ids = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids}&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        for item in data.get("items", []):
            video_id = item["id"]
            snippet = item["snippet"]
            content_details = item["contentDetails"]
            statistics = item["statistics"]
            video_data = {
                "video_id": video_id,
                "title": snippet["title"],
                "publishedAt": snippet["publishedAt"],
                "duration": content_details["duration"],
                "viewCount": statistics.get("viewCount", None),
                "likeCount": statistics.get("likeCount", None),
                "commentCount": statistics.get("commentCount", None)
                }
            video_details.append(video_data)
        return video_details
    except requests.exceptions.RequestException as e:
        raise e


if __name__ == "__main__":
    playlist_id = get_channel_playlist_id()
    video_ids = get_video_ids(playlist_id)
    print(extract_video_data(video_ids))