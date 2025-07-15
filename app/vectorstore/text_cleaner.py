import re

class TextCleaner:

    """
    Class for cleaning out embedding chunks and reducing 'noise' for the model to improve its performance.
    junk_words - most common unneccesary words often showing up in websites

    """

    def __init__(self):
        self.junk_words = [
            "home",
            "about",
            "contact",
            "privacy policy",
            "terms of service",
            "terms & conditions",
            "cookie policy",
            "sitemap",
            "copyright",
            "all rights reserved",
            "disclaimer",
            "faq",
            "frequently asked questions",
            "login",
            "sign up",
            "register",
            "subscribe",
            "newsletter",
            "follow us",
            "social media",
            "facebook",
            "twitter",
            "instagram",
            "linkedin",
            "youtube",
            "menu",
            "navigation",
            "search",
            "back to top",
            "read more",
            "submit",
            "©",
            "®",
            "™",
            "powered by",
            "designed by",
            "hosted by",
            "accessibility",
            "click here",
            "learn more",
            "terms",
            "policy",
            "support",
            "feedback",
            "careers",
            "blog",
            "help center"
        ]

        self._junk_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.junk_words)) + r')\b',
            flags=re.IGNORECASE
        )

    def remove_junk_words(self, text: str) -> str:
        """Remove all junk words from a text string."""
        removed_junk_text = self._junk_pattern.sub('', text)
        # Clean extra whitespace that may result from removals
        cleaned_text = ' '.join(removed_junk_text.split())
        return cleaned_text

    def remove_duplicates(self, text: str) -> str:
        # Split text by punctuation marks to get sentences roughly
        sentences = re.split(r'(?<=[.!?])\s+', text)
        seen = set()
        unique_sentences = []

        for sentence in sentences:
            s = sentence.strip()
            lower_s = s.lower()
            if lower_s and lower_s not in seen:
                unique_sentences.append(s)
                seen.add(lower_s)

        cleaned_text = ' '.join(unique_sentences)

        # Remove consecutive duplicate words
        cleaned_text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', cleaned_text, flags=re.IGNORECASE)

        return cleaned_text

    def clean(self, text: str) -> str:
        """Runs the full cleaning pipeline: remove junk words + remove duplicates."""
        text = self.remove_junk_words(text)
        text = self.remove_duplicates(text)
        return text