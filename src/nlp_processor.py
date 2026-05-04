import spacy
from collections import Counter

def _load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        raise OSError(
            "[ERROR] spaCy model not found. Run: python -m spacy download en_core_web_sm"
        )

nlp = _load_spacy_model()

DOMAIN_STOPWORDS = {
    "want", "like", "become", "work", "get", "make", "build",
    "learn", "know", "good", "great", "job", "career", "field",
    "interested", "looking", "trying", "need", "help", "start",
    "going", "time", "thing", "way", "people", "lot"
}


def process_input(user_text: str) -> dict:
    doc = nlp(user_text.lower().strip())

    tokens = [token.text for token in doc if not token.is_space]

    pos_tags = [
        (token.text, token.pos_, token.tag_)
        for token in doc
        if not token.is_space and not token.is_punct
    ]

    keywords = []
    for token in doc:
        if (
            token.pos_ in ("NOUN", "PROPN", "ADJ", "VERB")
            and not token.is_stop
            and not token.is_punct
            and not token.is_space
            and len(token.lemma_) > 2
            and token.lemma_ not in DOMAIN_STOPWORDS
        ):
            keywords.append(token.lemma_.lower())

    noun_chunks = [
        chunk.text.lower()
        for chunk in doc.noun_chunks
        if len(chunk.text.split()) > 1
    ]
    cleaned_tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and len(token.lemma_) > 2
    ]
    cleaned_text = " ".join(cleaned_tokens)

    return {
        "original": user_text,
        "tokens": tokens,
        "pos_tags": pos_tags,
        "keywords": keywords,
        "noun_chunks": noun_chunks,
        "cleaned_text": cleaned_text,
    }


def display_nlp_analysis(nlp_result: dict):
    print("\n" + "=" * 55)
    print("  NLP ANALYSIS")
    print("=" * 55)
    print(f"  Original Input : {nlp_result['original']}")
    print(f"  Cleaned Text   : {nlp_result['cleaned_text']}")
    print(f"\n  Extracted Keywords: {nlp_result['keywords']}")
    print(f"  Noun Chunks      : {nlp_result['noun_chunks']}")
    print(f"\n  POS Tags (token → POS → fine tag):")
    for token, pos, tag in nlp_result["pos_tags"]:
        print(f"    {token:<20} {pos:<10} {tag}")
    print("=" * 55)
