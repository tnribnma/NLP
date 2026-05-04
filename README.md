# Career Guidance System

This system provides career guidance based on user input, including NLP processing, career matching, roadmap generation, and resource recommendations.

## Features

- Natural Language Processing (NLP) to extract keywords and noun chunks from user input
- Career matching using TF-IDF and keyword overlap scoring
- Learning roadmap generation for top-matched careers
- Resource recommendation based on skills in the roadmap
- Visualization of results and errors

## Error Handling

The system provides informative error messages when:
- Input is empty or doesn't contain meaningful content
- Required data files (skills.json) are missing or invalid
- No career matches are found for the user's input
- NLP processing fails to extract meaningful terms
- Unexpected errors occur during execution

## Usage

Run the system with:
```bash
python3 main.py
```

Follow the prompt to describe your interests, background, and goals.

## Data Files

- `data/skills.json`: Contains career descriptions, keywords, and skills
- `data/resources.csv`: Contains learning resources (optional - system will warn if missing but continue)

## Output

Outputs are saved to the `output/` directory including:
- Roadmap JSON
- Visualization charts
- Error visualizations (when applicable)