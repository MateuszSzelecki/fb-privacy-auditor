"""Moduł 8: Słowa Klucze (TagCloud).

Analizuje teksty postów, komentarzy i wiadomości, aby stworzyć profil zainteresowań.
"""

from .module_template import BaseModule

class Module(BaseModule):

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy teksty Twoich postów i wiadomości",
            "Szukamy najczęściej używanych słów.",
            "Pomijamy stop-words i skupiamy się na rzeczownikach oraz przymiotnikach.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Słowa Klucze"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(TagCloud)"

    def panel_1(self) -> None:
        nouns = self.data.get("top_nouns") or ["muzyka", "polityka", "podróże", "sport"]
        self.add_table(
            rows=nouns,
            title="Najpopularniejsze rzeczowniki",
            columns=["Rzeczownik"]
        )

    def panel_2(self) -> None:
        adjectives = self.data.get("top_adjectives") or []
        self.add_table(
            rows=adjectives,
            title="Najpopularniejsze przymiotniki",
            columns=["Przymiotnik"],
        )

    def panel_3(self) -> None:
        words = self.data.get("speech_type_categorization") or {}
        self.add_bar_chart(data=words, title="Podział użytych słów")

    def panel_4(self) -> None:
        tag_scores = self.data.get("top_words") or {}

        self.add_table(
            rows=list(tag_scores.items()),
            title="Najpopularniejsze słowa",
            columns=["Słowo", "Ilość"],
        )

    def analyze(self) -> dict:
        import json
        import os
        from collections import Counter
        import string
        import spacy

        data_path: str = os.path.join("data", "your_facebook_activity")
        post_file_path: str = os.path.join(data_path, "posts", "your_posts__check_ins__photos_and_videos_1.json")
        message_base_path: str = os.path.join(data_path, "messages", "inbox")

        ignored_words: set[str] = {
            "i", "na", "w", "z", "nie", "się", "to", "że", "jest", "o", "dla", "jak", 
            "było", "być", "ten", "tego", "mnie", "tylko", "może", "już", "jestem"
        }

        # check for errors
        if not os.path.exists(post_file_path):
            return {"summary": "post file not found"}
        if not os.path.exists(message_base_path):
            return {"summary": "message file not found"}

        # load json data
        with open(post_file_path, "r", encoding="utf-8") as f:
            posts_data: dict = json.load(f)

        # form string of all used words in posts
        stored_text: str = ""
        for post in posts_data:
            if not "data" in post:
                continue
            for item in post["data"]:
                if not "post" in item:
                    continue
                # fix encoding issues
                raw_post = item["post"]
                try:
                    clean_post = raw_post.encode("latin1").decode("utf-8")
                except (UnicodeEncodeError, UnicodeDecodeError):
                    clean_post = raw_post
                stored_text += f" {clean_post}"

        # add message contents
        msg_count: int = 0
        # every user and group has assigned directory
        for chat_dir in os.listdir(message_base_path):
            contact_path: str = os.path.join(message_base_path, chat_dir)
            if not os.path.isdir(contact_path):
                continue
            # look for message files in contact directory
            for file in os.listdir(contact_path):
                if file.startswith("message_") and file.endswith(".json"):
                    msg_path: str = os.path.join(contact_path, file)
                    # get message contents
                    with open(msg_path, "r", encoding="utf-8") as f:
                        chat_data = json.load(f)
                        for msg in chat_data.get("messages", []):
                            if "content" in msg:
                                raw_msg = msg["content"]
                                # fix encoding issues
                                try:
                                    clean_msg = raw_msg.encode("latin1").decode("utf-8")
                                    stored_text += f" {clean_msg}"
                                    msg_count += 1
                                except:
                                    stored_text += f" {raw_msg}"

        # prepare used words for operations
        stored_text: str = stored_text.lower()
        stored_text: str = stored_text.translate(
            str.maketrans(string.punctuation, " " * len(string.punctuation))
        )
        words: list[str] = stored_text.split()
        words: list[str] = [w for w in words if len(w) > 3 and w not in ignored_words]

        # get statistics
        # based on Polish (spacy library)
        try:
            pll = spacy.load("pl_core_news_sm")
        except OSError:
            # install polish library if needed
            from spacy.cli.download import download as spacy_download

            spacy_download("pl_core_news_sm")
            pll = spacy.load("pl_core_news_sm")

        # there could be a lot of messages
        pll.max_length = 3000000

        # apperently this optimizes the process a little
        with pll.select_pipes(disable=["ner", "parser"]):
            doc = pll(" ".join(words))

        # get nouns and adjectives with spacy
        nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        adjectives = [token.text for token in doc if token.pos_ == "ADJ"]

        # get most frequently used
        top_nouns_counts = Counter(nouns).most_common(100)
        top_adj_counts = Counter(adjectives).most_common(100)
        top_word_counts = Counter(words).most_common(100)

        # update data structure
        results = {
            "top_nouns": [word for word in top_nouns_counts],
            "top_adjectives": [word for word in top_adj_counts],
            "top_words": dict(top_word_counts),
            "speech_type_categorization": {
                "Rzeczowniki": len(set(nouns)),
                "Przymiotniki": len(set(adjectives)),
            },
        }

        # add and return data
        self.data.update(results)
        return results
