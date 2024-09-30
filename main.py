import os
from collections import Counter
from halo import Halo
from git import Repo
import pandas as pd
import string
import unidecode
from prettytable import PrettyTable
from datetime import datetime

startTime = datetime.now()

spinnercheck = Halo(text="Required books found.", spinner="dots")
spinnerdownload = Halo(text="Cloning repository.", spinner="dots")


repo_url = "https://github.com/angelgarcan/course-python.git"
url_parts = repo_url.split("/")
username = url_parts[-2]
repo_name = url_parts[-1].replace(".git", "")
path = f"{username}_{repo_name}"
clone_dir = path
bookspath = os.path.join(clone_dir, "books", "gutenberg")


def librarian():
    try:
        if os.path.exists(path):
            spinnercheck.succeed()
            return
        spinnerdownload.start()
        Repo.clone_from(repo_url, clone_dir, depth=1)
        spinnerdownload.succeed()
    except Exception as e:
        print(f"Error: {e}")


def get_languages():
    languages = set()
    for root, dirs, files in os.walk(bookspath):
        for filename in files:
            if filename.endswith(".txt"):
                language = filename[:2]
                languages.add(language)
    return sorted(list(languages))


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.readlines()
            start_index = None
            end_index = None
            for i, line in enumerate(text):
                if line.startswith("*** START OF THIS PROJECT GUTENBERG EBOOK"):
                    start_index = i + 1
                elif line.startswith("*** END OF THIS PROJECT GUTENBERG EBOOK"):
                    end_index = i
                    break
            if start_index is not None and end_index is not None:
                return "".join(text[start_index:end_index])
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
    return ""


def mr_rogers():
    startTime_all = datetime.now()
    charcount_all = Counter()
    languages = get_languages()
    charexclusion = (
        string.punctuation
        + "\n\t\r"
        + " \u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u2028\u2029\u3000"
    )

    for root, dirs, files in os.walk(bookspath):
        for filename in files:
            if filename.endswith(".txt"):
                file_path = os.path.join(root, filename)
                text = read_file(file_path)
                text = unidecode.unidecode(text)
                text = "".join(c for c in text if c not in charexclusion)
                text = text.lower()
                charcount_all.update(text)

    df_all = pd.DataFrame(list(charcount_all.items()), columns=["Character", "Count"])
    df_all.sort_values(by="Count", ascending=False, inplace=True)
    df_all = df_all.reset_index(drop=True)
    format_dataframe(df_all.head(10), "Total character count across all files:")
    print(f"Total all books time: {datetime.now() - startTime_all}")

    for language in languages:
        startTime_lang = datetime.now()
        charcount = Counter()
        for root, dirs, files in os.walk(bookspath):
            for filename in files:
                if filename.startswith(language) and filename.endswith(".txt"):
                    file_path = os.path.join(root, filename)
                    text = read_file(file_path)
                    text = unidecode.unidecode(text)
                    text = "".join(c for c in text if c not in charexclusion)
                    text = text.lower()
                    charcount.update(text)

        if charcount:
            df_lang = pd.DataFrame(
                list(charcount.items()), columns=["Character", "Count"]
            )
            df_lang.sort_values(by="Count", ascending=False, inplace=True)
            df_lang = df_lang.reset_index(drop=True)
            format_dataframe(
                df_lang.head(10), f"Character count for '{language.upper()}':"
            )
            print(f"{language.upper()} books time: {datetime.now() - startTime_lang}")


def format_dataframe(df, title):
    table = PrettyTable()
    table.field_names = ["Character", "Count"]
    for index, row in df.iterrows():
        table.add_row([row["Character"], row["Count"]])
    print(f"\n{title}")
    print(table)


librarian()
get_languages()
mr_rogers()

print(f"Total book reading time: {datetime.now()-startTime}")
