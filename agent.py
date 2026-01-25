import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a lifestyle medicine health coach focused on helping people with chronic conditions make sustainable behavior changes.

You are:
- Proactive, not passive
- Focused on small, actionable steps
- Accountability-focused
- Warm but direct"""


def chat(user_message, health_context=""):
    messages = []
    
    if health_context:
        messages.append({
            "role": "user", 
            "content": f"Here's my health context:\n{health_context}"
        })
        messages.append({
            "role": "assistant",
            "content": "Got it. I'll keep this in mind."
        })
    
    messages.append({"role": "user", "content": user_message})
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    
    return response.content[0].text


if __name__ == "__main__":
    context = "42 years old, hypertension, desk job, poor sleep"
    response = chat("Where do I start?", context)
    print(response)