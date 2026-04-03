"""Core conversational health coach agent."""

import json

import anthropic
from dotenv import load_dotenv

from .prompts import build_system_prompt, MEMORY_EXTRACTION_PROMPT
from .memory import get_profile_summary, save_patient

load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"
EXTRACTION_MODEL = "claude-haiku-4-5-20251001"  # Lighter model for structured extraction


def chat(user_message, profile, conversation_history):
    """Send a message and get a coaching response.

    Args:
        user_message: The patient's message
        profile: The patient's full profile dict
        conversation_history: List of {"role": ..., "content": ...} dicts

    Returns:
        (assistant_response, updated_conversation_history)
    """
    system_prompt = build_system_prompt(profile)

    # Build messages: include recent history for continuity
    messages = list(conversation_history[-12:])  # Last 6 exchanges
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )

    assistant_text = response.content[0].text

    # Update history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": assistant_text})

    return assistant_text, conversation_history


def extract_profile_updates(user_message, assistant_response, profile):
    """Use Claude to extract structured updates from a conversation exchange.

    Returns a dict with potential updates to the patient profile.
    """
    profile_summary = get_profile_summary(profile)

    prompt = MEMORY_EXTRACTION_PROMPT.format(
        user_message=user_message,
        assistant_response=assistant_response,
        profile_summary=profile_summary
    )

    try:
        response = client.messages.create(
            model=EXTRACTION_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        # Handle markdown code blocks
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        updates = json.loads(text)
        return updates
    except (json.JSONDecodeError, IndexError, KeyError):
        return {}


def apply_profile_updates(profile, updates):
    """Apply extracted updates to a patient profile."""
    if not updates:
        return profile

    # Update health info in demographics notes
    new_info = updates.get("new_health_info")
    if new_info and isinstance(new_info, str) and new_info.strip():
        existing_notes = profile.get("demographics", {}).get("notes", "")
        # Avoid duplicate info
        if new_info.lower() not in existing_notes.lower():
            profile["demographics"]["notes"] = (
                f"{existing_notes} {new_info}".strip() if existing_notes else new_info
            )

    # Add new goal if mentioned
    new_goal = updates.get("new_goal")
    if isinstance(new_goal, dict) and new_goal.get("description"):
        from .memory import add_goal
        add_goal(
            profile,
            pillar=new_goal.get("pillar", "other"),
            description=new_goal["description"],
            target=new_goal.get("target", ""),
            timeframe=new_goal.get("timeframe", "")
        )

    # Update existing goal if check-in reported
    goal_update = updates.get("goal_update")
    if isinstance(goal_update, dict) and goal_update.get("description"):
        desc = goal_update["description"].lower()
        for goal in profile.get("goals", []):
            if goal.get("status") == "active" and desc in goal.get("description", "").lower():
                from .memory import check_in_goal
                check_in_goal(
                    profile,
                    goal["id"],
                    goal_update.get("adherence", False),
                    goal_update.get("notes", "")
                )
                break

    save_patient(profile)
    return profile
