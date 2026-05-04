import json
import os
import math
from datetime import datetime

class RoadmapError(Exception):
    pass

SKILL_TIERS = {
    "foundation": 1,
    "core":       2,
    "advanced":   3,
}
FOUNDATION_SKILLS = {
    "python", "git", "linux", "bash", "html", "css", "dart",
    "sql", "networking", "statistics", "regex"
}
ADVANCED_SKILLS = {
    "transformers", "kubernetes", "terraform", "scala basics",
    "penetration testing", "mlops", "deep learning",
    "real-time streaming", "system design", "research skills"
}

def _classify_skill(skill: str) -> str:
    s = skill.lower()
    if s in FOUNDATION_SKILLS:
        return "foundation"
    if s in ADVANCED_SKILLS:
        return "advanced"
    return "core"


def _distribute_skills_to_weeks(skills: list[str], total_weeks: int) -> dict:
    tiered = sorted(skills, key=lambda s: SKILL_TIERS[_classify_skill(s)])

    skills_per_week = math.ceil(len(tiered) / total_weeks)
    schedule = {}
    for week in range(1, total_weeks + 1):
        start = (week - 1) * skills_per_week
        end = start + skills_per_week
        week_skills = tiered[start:end]
        if week_skills:
            schedule[week] = week_skills

    return schedule

def generate_roadmap(
    career: str,
    skills_path: str,
    total_weeks: int = 8,
    known_skills: list[str] = None,
) -> dict:
    try:
        with open(skills_path, "r") as f:
            career_data = json.load(f)
    except FileNotFoundError:
        raise RoadmapError(f"Skills file not found: {skills_path}")
    except json.JSONDecodeError as e:
        raise RoadmapError(f"Invalid JSON in skills file: {e}")

    if career not in career_data:
        available = ", ".join(career_data.keys())
        raise RoadmapError(f"Career '{career}' not found. Available: {available}")

    if total_weeks not in (4, 8, 12):
        raise RoadmapError(f"total_weeks must be 4, 8, or 12. Got: {total_weeks}")

    data = career_data[career]
    all_skills = data["skills"]

    known_lower = set(s.strip().lower() for s in (known_skills or []))
    skipped_skills = []
    remaining_skills = []

    for skill in all_skills:
        if skill.lower() in known_lower:
            skipped_skills.append(skill)
        else:
            remaining_skills.append(skill)

    '''if not remaining_skills:
        remaining_skills = all_skills  '''
    try:
        schedule = _distribute_skills_to_weeks(remaining_skills, total_weeks)
    except Exception as e:
        raise RoadmapError(f"Failed to distribute skills: {e}")

    weekly_plan = []
    for week_num in range(1, total_weeks + 1):
        week_skills = schedule.get(week_num, [])
        if not week_skills:
            continue

        tier = _classify_skill(week_skills[0])
        daily_focus = _create_daily_breakdown(week_skills, week_num, tier)

        weekly_plan.append({
            "week": week_num,
            "tier": tier,
            "theme": _get_week_theme(week_num, total_weeks, tier),
            "skills": week_skills,
            "skill_count": len(week_skills),
            "daily_breakdown": daily_focus,
            "goal": f"Complete foundational understanding of: {', '.join(week_skills)}",
        })

    roadmap = {
        "meta": {
            "career": career,
            "career_display": career.replace("_", " ").title(),
            "description": data["description"],
            "total_weeks": total_weeks,
            "total_skills": len(all_skills),
            "skipped_skills": skipped_skills,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "weekly_plan": weekly_plan,
        "summary": {
            "foundation_weeks": sum(1 for w in weekly_plan if w["tier"] == "foundation"),
            "core_weeks":       sum(1 for w in weekly_plan if w["tier"] == "core"),
            "advanced_weeks":   sum(1 for w in weekly_plan if w["tier"] == "advanced"),
            "skills_per_week":  [len(w["skills"]) for w in weekly_plan],
        }
    }

    return roadmap


def _create_daily_breakdown(skills: list[str], week: int, tier: str) -> list[str]:
    if len(skills) == 1:
        skill = skills[0]
        return [
            f"Day 1: Introduction & setup for {skill}",
            f"Day 2: Core concepts and theory",
            f"Day 3: Hands-on practice & examples",
            f"Day 4: Mini project / exercises",
            f"Day 5: Review, notes & quiz",
        ]
    return [
        f"Day 1-2: {skills[0]} — theory & practice",
        f"Day 3-4: {skills[1] if len(skills) > 1 else skills[0]} — theory & practice",
        f"Day 5: Review all skills + mini project",
    ]


def _get_week_theme(week: int, total: int, tier: str) -> str:
    if tier == "foundation":
        return "Building Foundations"
    if tier == "advanced":
        return "Advanced Mastery"
    if week <= total // 2:
        return "Core Skill Development"
    return "Deepening Knowledge"


def save_roadmap_json(roadmap: dict, output_path: str = "roadmap_output.json"):
    with open(output_path, "w") as f:
        json.dump(roadmap, f, indent=2)
    print(f"\n Roadmap saved to: {output_path}")


def display_roadmap(roadmap: dict):
    meta = roadmap["meta"]
    print("\n" + "=" * 55)
    print(f"  ROADMAP: {meta['career_display'].upper()}")
    print("=" * 55)
    print(f"  {meta['description']}")
    print(f"  Duration  : {meta['total_weeks']} weeks")
    print(f"  Skills    : {meta['total_skills']} to learn")
    if meta["skipped_skills"]:
        print(f"  Skipped   : {', '.join(meta['skipped_skills'])} (you know these)")
    print(f"  Generated : {meta['generated_at']}")
    print()

    for week in roadmap["weekly_plan"]:
        tier_icon = {
            "foundation": "\033[94m[FOUNDATION]\033[0m",
            "core": "\033[93m[CORE]\033[0m",
            "advanced": "\033[91m[ADVANCED]\033[0m"
        }.get(week["tier"], "\033[90m[UNKNOWN]\033[0m")
        print(f"  Week {week['week']:>2} {tier_icon}  [{week['theme']}]")
        print(f"         Skills: {', '.join(week['skills'])}")
        print()

    s = roadmap["summary"]
    print(f"  Summary → Foundation: {s['foundation_weeks']}w | "
          f"Core: {s['core_weeks']}w | Advanced: {s['advanced_weeks']}w")
    print("=" * 55)
