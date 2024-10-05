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
    languages = get_languages()
    charexclusion = (
        string.punctuation
        + "\n\t\r"
        + " \u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u2028\u2029\u3000"
    )

    largest_files = {}
    for root, dirs, files in os.walk(bookspath):
        for filename in files:
            if filename.endswith(".txt"):
                language = filename[:2]
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                if (
                    language not in largest_files
                    or file_size > largest_files[language][1]
                ):
                    largest_files[language] = (file_path, file_size)

    output = os.path.join("output.txt")
    with open(output, "w", encoding="utf-8") as file:
        for language, (file_path, _) in largest_files.items():
            filename = os.path.basename(file_path)
            print(filename)
            charcount = Counter()
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

                result = f"\n\nCharacter count for '{language.upper()}':\n"
                result += df_lang.head(10).to_string(index=False)

                print(f"\n\nCharacter count for '{language.upper()}':")
                format_dataframe(df_lang.head(10), "")
                file.write(result)


def format_dataframe(df, title):
    table = PrettyTable()
    table.field_names = ["Character", "Count"]
    for index, row in df.iterrows():
        table.add_row([row["Character"], row["Count"]])
    print(f"{title}")
    table.align["Count"] = "r"
    print(table)


def main():
    get_books()
    get_languages()
    count_char()


if __name__ == "__main__":
    main()
