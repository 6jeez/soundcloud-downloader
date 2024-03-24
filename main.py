import os
import time
import requests
from playwright.sync_api import sync_playwright


def download_file(url, file_path):
    response = requests.get(url)
    with open(file_path, "wb") as file:
        file.write(response.content)


def download_from_soundcloud(url, name, download_folder):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto("https://soundcloudmp3.org/ru")

            page.fill('input[name="url"]', url)

            page.click('button[name="submit"]')

            time.sleep(5)

            download_link = page.query_selector(
                'a#download-btn').get_attribute('href')

            browser.close()
    except Exception as ex:
        print(f"Error while parsing: {ex}")

    try:
        clean_name = name.replace('/', ' ')
        download_file(url=download_link, file_path=f'{download_folder}/{clean_name}.mp3')
        print(f"[SUCCESSFULLY] {name}")
    except Exception as ex:
        print(f"[ERROR]{name} ! {ex}")


def scraper(playlist_link, scrape_range=50):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(playlist_link)

        for _ in range(scrape_range):
            time.sleep(0.2)
            page.evaluate('window.scrollBy(0, window.innerHeight * 0.2)')

        print("The page is fully scrolled down")

        songs_info = []

        track_links = page.query_selector_all("a.trackItem__trackTitle")
        for track_link in track_links:
            link = track_link.get_attribute("href")
            text = track_link.inner_text()
            songs_info.append((text, link))

        with open("songs_info.txt", "w", encoding="utf-8") as file:
            for text, link in songs_info:
                file.write(f"{text}: https://soundcloud.com{link}\n")

        print(f"Found {len(songs_info)} songs")

        time.sleep(5)
        browser.close()


def download_from_file(folder_path):
    with open('songs_info.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        name, url = line.split(':', 1)
        download_from_soundcloud(url=url, name=name, download_folder=folder_path)


if __name__ == "__main__":
    print("what you want:\n[1] Download from file\n[2] Scrape songs from playlist")
    answer = input('your answer: ')
    if answer == '1':
        folder_path = input('Enter folder path for download: ')
        if os.path.exists(folder_path):
            download_from_file(folder_path=folder_path)
        else:
            os.makedirs(name=folder_path)
            download_from_file(folder_path=folder_path)
    elif answer == '2':
        scrape_range = int(input('Enter scrape range(def=50): '))
        playlist_url = input('Enter playlist url: ')

        scraper(playlist_link=playlist_url, scrape_range=scrape_range)
