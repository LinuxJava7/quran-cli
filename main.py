import requests
import time
import re
from art import *
import os
import json

# Function to read constants from the config file
def read_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)


def main_app():
    tprint("quran-cli")
    print("A simple Quran reader in CLI.\n")
    main_menu()


def main_menu():
    config = read_config()  # Read config constants
    global bullet_point
    bullet_point = 0
    global txt

    print("Main menu:")
    print("1. Chapter reading mode (Sahih International)")
    print("2. Write to a new file")
    print("3. Create HTML (WARNING: HIGHLY EXPERIMENTAL)")
    print("4. Create Markdown (WARNING: EXPERIMENTAL)")

    while True:
        command = input("Input your option: ")
        try:
            command = int(command)
            if command in [1, 2, 3, 4]:
                break
            else:
                print("Invalid option. Please choose a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    match command:
        case 1:
            user_chapter = input("Which chapter? ")
            txt = 1
            get_translation(user_chapter, None, config)
        case 2:
            file = input("What should be the name of the txt file? ")
            user_chapter = input("Which chapter? ")
            txt = 2
            get_translation(user_chapter, file, config)
        case 3:
            file = input("What should be the name of the HTML file? ")
            user_chapter = input("Which chapter? ")
            txt = 3
            get_translation(user_chapter, file, config)
        case 4:
            file = input("What should be the name of the Markdown file? ")
            user_chapter = input("Which chapter? ")
            bullet_point = int(input(config["bullet_point_symbols"] + ": "))
            if bullet_point not in [1, 2]:
                exit()
            txt = 4
            get_translation(user_chapter, file, config)
        case other:
            print("Sorry, incorrect option.")


def get_translation(user_chapter, Filename, config):
    response = requests.get(f"{config['api_base_url']}{config['chapters_endpoint']}/{user_chapter}")

    dict = response.json()
    table = dict['chapter']
    names = table['translated_name']

    print("\nChapter: '{}/{}': '{}' ({} verses):\n".format(
        table['name_arabic'], table['name_complex'], names['name'],
        table['verses_count']))
    match txt:
        case 1:
            get_translated_verses(user_chapter, table['verses_count'], config)
        case 2:
            Get_it(user_chapter, table['verses_count'], Filename, "txt", config, names)
        case 3:
            HTML_CONVERT(user_chapter, table['verses_count'], Filename, config)
        case 4:
            Get_it(user_chapter, table['verses_count'], Filename, "md", config, names)


def get_translated_verses(user_chapter, verse_number, config):
    response = requests.get(
        f"{config['api_base_url']}{config['translations_endpoint']}?chapter_number={user_chapter}"
    )

    dict = response.json()
    table = dict['translations']

    i = 0
    while i < verse_number:

        eggs = table[i]
        ayah = eggs['text']
        formatted_ayah = re.sub('<sup foot_note=\d+>\d+<\/sup>', '', ayah)
        print(f"{i+1}. {formatted_ayah}\n")
        time.sleep(len(formatted_ayah) * 0.02)
        i += 1


def Get_it(user_chapter, verse_number, Filename, filetype, config, names):
    path = f"{config['output_directory']}/{filetype}"
    if not os.path.exists(path):
        os.makedirs(path)

    f = open(f"{path}/{Filename}.{filetype}", "w")
    if filetype == "md":
        f.write(
            f"# Chapter: '{names['name']}' ({verse_number} verses)\n\n"
        )
    f.close()
    response = requests.get(
        f"{config['api_base_url']}{config['translations_endpoint']}?chapter_number={user_chapter}"
    )

    dict = response.json()
    table = dict['translations']

    i = 0
    while i < verse_number:

        eggs = table[i]
        ayah = eggs['text']
        formatted_ayah = re.sub('<sup foot_note=\d+>\d+<\/sup>', '', ayah)
        print(f"{i+1}/{verse_number} Successfully Copied!\n")
        f = open(f"{path}/{Filename}.{filetype}", "a")
        if bullet_point == 1 or bullet_point == 0:
            f.write(f"{i+1}. {formatted_ayah}\n\n")
        elif bullet_point == 2:
            f.write(f"* {formatted_ayah}\n\n")
        f.close()
        i += 1
    print(f"Done! File outputted at {path}/{Filename}.{filetype}")


def HTML_CONVERT(user_chapter, verse_number, Filename, config):
    path = f"{config['output_directory']}/html"
    if not os.path.exists(path):
        os.makedirs(path)

    f = open(f"{path}/{Filename}.html", "a")
    w(f, "<head>")
    w(f, config["html_css_link"])
    w(f, "</head>")
    w(f, "<style>")
    w(f, config["html_style"])
    w(f, "</style>")

    f.close()
    response = requests.get(
        f"{config['api_base_url']}{config['translations_endpoint']}?chapter_number={user_chapter}"
    )

    dict = response.json()
    table = dict['translations']
    NewFile = "{}/{}.html".format(path, Filename)

    i = 0
    while i < verse_number:

        eggs = table[i]
        ayah = eggs['text']
        formatted_ayah = re.sub('<sup foot_note=\d+>\d+<\/sup>', '', ayah)
        print(f"{i+1}/{verse_number} Successfully Copied!\n")

        f = open(NewFile, "a")
        w(f, "<p>")
        f.write(f"{i+1}. {formatted_ayah}\n")
        w(f, "</p>")
        f.close()
        i += 1
    print(f"Done! File outputted at {path}/{Filename}.html")


def w(f, string):
    f.write(f"{string}\n")


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main_app()
