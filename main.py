import os
from collections import Counter
from git import Repo
import pandas as pd
import string
from prettytable import PrettyTable
from datetime import datetime

pd.options.display.float_format = "{:,}".format

repo_url = "https://github.com/angelgarcan/course-python.git"
url_parts = repo_url.split("/")
username = url_parts[-2]
repo_name = url_parts[-1].replace(".git", "")
path = f"{username}_{repo_name}"
clone_dir = path
bookspath = os.path.join(clone_dir, "books", "gutenberg")


def get_books():
    try:
        if os.path.exists(path):
            return
        Repo.clone_from(repo_url, clone_dir, depth=1)
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


def normalize_char(s):
    mapping = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "ä": "a",
        "ë": "e",
        "ï": "i",
        "ö": "o",
        "ü": "u",
    }
    return "".join(mapping.get(c, c) for c in s)


def count_char():
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
                text = "".join(c for c in text if c not in charexclusion)
                text = text.lower()
                text = normalize_char(text)
                charcount_all.update(text)

    df_all = pd.DataFrame(list(charcount_all.items()), columns=["Character", "Count"])
    df_all["Count"] = df_all["Count"].astype(int)
    df_all.sort_values(by="Count", ascending=False, inplace=True)
    df_all = df_all.reset_index(drop=True)
    df_all["Count"] = df_all["Count"].map("{:,}".format)
    format_dataframe(df_all.head(10), "Total character count across all files:")

    for language in languages:
        charcount = Counter()
        for root, dirs, files in os.walk(bookspath):
            for filename in files:
                if filename.startswith(language) and filename.endswith(".txt"):
                    file_path = os.path.join(root, filename)
                    text = read_file(file_path)
                    text = "".join(c for c in text if c not in charexclusion)
                    text = text.lower()
                    text = normalize_char(text)
                    charcount.update(text)

        if charcount:
            df_lang = pd.DataFrame(
                list(charcount.items()), columns=["Character", "Count"]
            )
            df_lang["Count"] = df_lang["Count"].astype(int)
            df_lang.sort_values(by="Count", ascending=False, inplace=True)
            df_lang = df_lang.reset_index(drop=True)
            df_lang["Count"] = df_lang["Count"].map("{:,}".format)
            format_dataframe(
                df_lang.head(10), f"Character count for '{language.upper()}':"
            )


def format_dataframe(df, title):
    table = PrettyTable()
    table.field_names = ["Character", "Count"]
    for index, row in df.iterrows():
        table.add_row([row["Character"], row["Count"]])
    print(f"\n{title}")
    table.align["Count"] = "r"
    print(table)


def main():
    get_books()
    get_languages()
    count_char()


if __name__ == "__main__":
    main()
