import csv

class ResourceError(Exception):
    pass

def load_resources(resources_path: str) -> list[dict]:
    try:
        resources = []
        with open(resources_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                resources.append(row)
        return resources
    except FileNotFoundError:
        raise ResourceError(f"Resources file not found: {resources_path}")
    except KeyError as e:
        raise ResourceError(f"Missing required column in resources CSV: {e}")

def _skill_matches_topic(skill: str, topic: str) -> bool:
    skill_l = skill.lower().strip()
    topic_l = topic.lower().strip()

    if skill_l == topic_l:
        return True

    if skill_l in topic_l or topic_l in skill_l:
        return True

    skill_words = set(skill_l.split())
    topic_words = set(topic_l.split())
    common = skill_words & topic_words
    if common and any(len(w) > 3 for w in common):
        return True

    return False

def recommend_resources(skills: list[str], resources_path: str) -> dict:
    all_resources = load_resources(resources_path)
    recommendations = {}

    for skill in skills:
        matches = []
        for res in all_resources:
            if _skill_matches_topic(skill, res["topic"]):
                matches.append({
                    "name": res["resource_name"],
                    "type": res["type"],
                    "url": res["url"],
                    "difficulty": res["difficulty"],
                })
        matches_sorted = sorted(
            matches,
            key=lambda x: {"beginner": 0, "intermediate": 1, "advanced": 2}.get(x["difficulty"], 1)
        )
        recommendations[skill] = matches_sorted[:2]

    return recommendations

def display_resources(recommendations: dict):
    st.markdown("Learning Resources")
    for skill, resources in recommendations.items():
        st.subheader(skill)

        if not resources:
            st.warning("No resources found — search on Google/YouTube")
            continue

        for r in resources:
            st.markdown(f"[{r['type'].upper()}] {r['name']} ({r['difficulty']})")
            st.markdown(f" {r['url']}")

        st.divider()
