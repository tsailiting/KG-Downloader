import os
import json
import requests


class KSongScraper:
    DOWNLOAD_PATH = "downloads"
    TEXT_BEFORE_JSON = "window.__DATA__ = "
    TEXT_AFTER_JSON = "; </script>"

    def __init__(self, download_path=None):
        self.download_path = download_path or self.DOWNLOAD_PATH
        self.data = {}

    def fetch_page(self, url):
        """從網址獲取 HTML 內容"""
        print(f"Fetching {url} ...")
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch page, status code: {response.status_code}")
        return response.text

    def extract_json_data(self, content):
        """從 HTML 提取 JSON 數據"""
        start_idx = content.find(self.TEXT_BEFORE_JSON)
        if start_idx == -1:
            raise ValueError("Could not find song data in the page")

        content = content[start_idx + len(self.TEXT_BEFORE_JSON):]
        end_idx = content.find(self.TEXT_AFTER_JSON)
        if end_idx == -1:
            raise ValueError("Could not extract valid JSON from page")

        return json.loads(content[:end_idx])

    def parse(self, url):
        """解析歌曲頁面，提取所有歌曲資訊"""
        content = self.fetch_page(url)
        self.data = self.extract_json_data(content)

        # 提取所有歌曲資訊
        detail = self.data.get("detail", {})

        # 打印出所有可用的資訊
        print("\n=== 完整歌曲資訊 ===")
        for key, value in detail.items():
            print(f"{key}: {value}")

        # 整理成字典
        song_info = {
            "song_name": detail.get("song_name", "Unknown"),
            "play_url": detail.get("playurl", "N/A"),
            "singer": detail.get("nick", "Unknown"),
            "song_id": detail.get("song_id", "Unknown"),
            "cover": detail.get("cover", "N/A"),
            "comment_count": detail.get("comment_cnt", 0),
            "like_count": detail.get("like_cnt", 0),
            "share_count": detail.get("share_cnt", 0),
            "play_count": detail.get("play_cnt", 0),
            "duration": detail.get("duration", 0),
        }

        # 存成 JSON 檔案
        json_path = os.path.join(
            self.download_path, f"{song_info['song_name']}.json")
        os.makedirs(self.download_path, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(song_info, f, ensure_ascii=False, indent=4)

        print(f"\n🎵 歌曲資訊已存檔: {json_path}")

        return song_info

    def download_audio(self):
        """下載歌曲音訊"""
        play_url = self.data.get("detail", {}).get("playurl")
        song_name = self.data.get("detail", {}).get("song_name", "unknown")

        if not play_url or play_url == "N/A":
            print("No valid play URL found, skipping download.")
            return

        print(f"Downloading {song_name}...")
        response = requests.get(play_url)
        audio_path = os.path.join(self.download_path, f"{song_name}.m4a")

        with open(audio_path, "wb") as f:
            f.write(response.content)

        print(f"Download finished: {audio_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KSong Scraper")
    parser.add_argument("url", type=str, help="URL of the song page")

    args = parser.parse_args()

    scraper = KSongScraper()
    song_data = scraper.parse(args.url)

    print("\n=== 提取的歌曲資訊 ===")
    print(json.dumps(song_data, indent=4, ensure_ascii=False))
