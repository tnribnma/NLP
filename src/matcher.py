import json
import math

class MatcherError(Exception):
    pass

def _build_vocabulary(corpus):
    vocab = set()
    for doc in corpus:
        for word in doc.split():
            vocab.add(word)
    return sorted(vocab)

def _tf(term, doc):
    words = doc.split()
    return words.count(term) / len(words) if words else 0.0

def _idf(term, corpus):
    n = sum(1 for doc in corpus if term in doc.split())
    if n == 0:
        return 0.0
    return math.log((1 + len(corpus)) / (1 + n)) + 1

def _tfidf_vector(doc, vocab, idf_values):
    return [_tf(term, doc) * idf_values.get(term, 0) for term in vocab]

def _cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a ** 2 for a in vec_a))
    norm_b = math.sqrt(sum(b ** 2 for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class CareerMatcher:

    def __init__(self, skills_path: str):
        try:
            with open(skills_path, "r") as f:
                self.career_data = json.load(f)
        except FileNotFoundError:
            raise MatcherError(f"Skills file not found: {skills_path}")
        except json.JSONDecodeError as e:
            raise MatcherError(f"Invalid JSON in skills file: {e}")

        if not self.career_data:
            raise MatcherError("Skills file is empty or invalid")

        self.career_names = list(self.career_data.keys())
        self.career_docs = []
        for career, data in self.career_data.items():
            combined = (
                career.replace("_", " ") + " " +
                data["description"] + " " +
                " ".join(data["keywords"]) + " " +
                " ".join(data["skills"]).lower()
            )
            self.career_docs.append(combined.lower())

        self.vocab = _build_vocabulary(self.career_docs)
        self.idf_values = {term: _idf(term, self.career_docs) for term in self.vocab}
        self.career_vectors = [
            _tfidf_vector(doc, self.vocab, self.idf_values)
            for doc in self.career_docs
        ]

    def _keyword_overlap_score(self, user_keywords, career):
        data = self.career_data[career]
        career_terms = set(kw.lower() for kw in data["keywords"] + data["skills"])
        if not user_keywords:
            return 0.0
        matches = sum(1 for kw in user_keywords if kw in career_terms)
        return matches / len(user_keywords)

    def match(self, nlp_result: dict, top_n: int = 3) -> list[dict]:
        try:
            cleaned_text = nlp_result.get("cleaned_text", "")
            user_keywords = nlp_result.get("keywords", []) + nlp_result.get("noun_chunks", [])

            if not cleaned_text:
                raise MatcherError("No cleaned text found in NLP result")

            user_vector = _tfidf_vector(cleaned_text, self.vocab, self.idf_values)

            scores = []
            for i, career in enumerate(self.career_names):
                tfidf_score = _cosine_similarity(user_vector, self.career_vectors[i])
                kw_score = self._keyword_overlap_score(user_keywords, career)
                hybrid_score = 0.6 * tfidf_score + 0.4 * kw_score
                scores.append({
                    "career": career,
                    "tfidf_score": round(tfidf_score, 4),
                    "keyword_score": round(kw_score, 4),
                    "hybrid_score": round(hybrid_score, 4),
                })

            scores.sort(key=lambda x: x["hybrid_score"], reverse=True)
            top = scores[:top_n]

            MINIMUM_SCORE = 0.05
            if not top or top[0]["hybrid_score"] < MINIMUM_SCORE:
                raise MatcherError(
                    "Roadmap not found: your input did not match any career in our "
                    "database. Try describing your interests with more specific technical "
                    "keywords (e.g. 'machine learning', 'web development', 'cybersecurity')."
                )
            max_score = top[0]["hybrid_score"]
            for item in top:
                raw_pct = (item["hybrid_score"] / max_score) * 100
                item["confidence_pct"] = round(raw_pct, 1)

            return top

        except MatcherError:
            raise
        except KeyError as e:
            raise MatcherError(f"Missing NLP data: {e}")
        except Exception as e:
            raise MatcherError(f"Matching failed: {e}")
