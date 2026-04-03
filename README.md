# Health Coach Agent

A clinical lifestyle medicine coaching agent that uses validated assessments, SMART goal tracking, and evidence-based behavior change techniques to help patients with chronic conditions make sustainable lifestyle modifications.

Built to combat **clinical inertia** — the gap between what patients know they should do and what they actually do between visits.

## Why This Matters for Clinical Research

Traditional health coaching is expensive, hard to scale, and difficult to study systematically. This agent provides:

- **Validated screening instruments** (PHQ-2, GAD-2, Exercise Vital Sign, Sleep Quality, Dietary Assessment, Perceived Stress) with automated scoring and interpretation
- **Longitudinal tracking** — assessment scores, goal adherence, and session notes over time
- **Structured data export** (CSV) for research analysis — assessment trajectories, goal adherence rates, session SOAP notes
- **SOAP note documentation** — auto-generated clinical session summaries
- **Reproducible coaching protocol** — consistent evidence-based approach across all patients

## Quick Start

```bash
# Clone and set up
git clone https://github.com/ajinrane/health-coach-agent.git
cd health-coach-agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run
python main.py
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `/assess` | Run a validated clinical screening instrument |
| `/goals` | View all goals with adherence stats |
| `/newgoal` | Create a new SMART goal |
| `/checkin` | Check in on goal progress |
| `/complete` | Mark a goal as completed |
| `/profile` | View your full health profile |
| `/session` | View current session summary |
| `/history` | View past session summaries with SOAP notes |
| `/export` | Export all data to CSV for research analysis |
| `/help` | Show available commands |
| `/quit` | End session, generate SOAP note, save |

Or just type naturally to talk to your coach.

## Clinical Assessments

All instruments are validated, publicly available screening tools used in primary care:

- **PHQ-2** — Depression screening (Kroenke et al., 2003)
- **GAD-2** — Anxiety screening (Kroenke et al., 2007)
- **Exercise Vital Sign** — Physical activity assessment (Coleman et al., 2012)
- **Sleep Quality Screen** — Based on PSQI domains (Buysse et al., 1989)
- **Brief Dietary Assessment** — Based on MEDAS (Schröder et al., 2011)
- **Perceived Stress Screen** — Based on PSS (Cohen et al., 1983)

## Architecture

```
health-coach-agent/
├── main.py                 # CLI entry point
├── coach/
│   ├── agent.py            # Core conversational agent
│   ├── prompts.py          # System prompts and templates
│   ├── memory.py           # Patient profile management
│   ├── session.py          # Session tracking and SOAP notes
│   ├── assessments.py      # Validated clinical instruments
│   ├── goals.py            # SMART goal tracking
│   └── export.py           # Research data export (CSV)
├── data/
│   ├── patients/           # Patient profiles (gitignored)
│   ├── sessions/           # Session logs (gitignored)
│   └── exports/            # CSV exports (gitignored)
├── requirements.txt
└── README.md
```

## Behavior Change Framework

The agent uses techniques from:
- **Motivational Interviewing** — OARS (Open questions, Affirmations, Reflections, Summaries)
- **Implementation Intentions** — "When [situation], I will [behavior]" (Gollwitzer, 1999)
- **Self-Determination Theory** — Supporting autonomy, competence, relatedness (Deci & Ryan, 2000)
- **Habit Stacking** — Attaching new behaviors to existing routines (Clear, 2018)

## Data Export for Research

Run `/export` to generate CSV files:
- `assessment_trajectories_*.csv` — Longitudinal assessment scores across patients
- `goal_adherence_*.csv` — Goal-level adherence data with check-in history
- `session_notes_*.csv` — SOAP notes from all sessions

## Legacy Files

The original single-file implementations are preserved for reference:
- `agent.py` — Basic single-turn agent
- `cli.py` — Interactive CLI without persistence
- `memory_cli.py` — CLI with JSON memory (predecessor to current system)

## License

MIT
