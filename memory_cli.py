import anthropic
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a lifestyle medicine health coach grounded in evidence-based research.

RULES:
1. NEVER ask more than one question per response
2. Give specific, actionable advice immediately
3. Keep responses under 100 words
4. When giving advice, cite the evidence briefly

EVIDENCE BASE YOU DRAW FROM:
- Sleep: Adults need 7-9 hours. Poor sleep linked to weight gain, insulin resistance, cardiovascular risk (Walker, 2017; Cappuccio et al., Sleep Medicine Reviews)
- Exercise: 150 min moderate or 75 min vigorous per week. Resistance training 2x/week. Even 10-min walks improve metabolic health (WHO Guidelines; Stamatakis et al., JAMA Internal Medicine 2022)
- Nutrition: Mediterranean and DASH diets have strongest evidence for cardiovascular health (Estruch et al., NEJM 2018)
- Stress: Chronic stress elevates cortisol, disrupts sleep, increases visceral fat (McEwen, NEJM 1998)
- Hydration: 2-3L daily for most adults; more with exercise (EFSA guidelines)
- Strength training: Preserves muscle mass, improves insulin sensitivity, bone density (Westcott, Current Sports Medicine Reports 2012)

EXAMPLE RESPONSE:
"Start with a 10-minute walk after dinner tonight. Research shows even short walks significantly improve post-meal blood sugar (Estruch et al., JAMA 2022). How does that feel as a first step?"

Your job is to get them DOING, not keep them TALKING."""

MEMORY_FILE = "user_memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "health_context": "",
            "goals": [],
            "actions_taken": [],
            "conversation_history": []
        }

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def chat(user_message, memory):
    # Build context from memory
    context_summary = f"""
USER PROFILE:
- Health context: {memory['health_context']}
- Goals: {', '.join(memory['goals']) if memory['goals'] else 'Not set yet'}
- Recent actions: {', '.join(memory['actions_taken'][-3:]) if memory['actions_taken'] else 'None yet'}
"""
    
    # Include recent conversation history
    messages = []
    
    # Add memory context
    messages.append({
        "role": "user",
        "content": f"Here's what you know about me:\n{context_summary}"
    })
    messages.append({
        "role": "assistant",
        "content": "Got it, I remember you. Let's continue."
    })
    
    # Add recent conversation history (last 6 exchanges)
    for exchange in memory["conversation_history"][-6:]:
        messages.append({"role": "user", "content": exchange["user"]})
        messages.append({"role": "assistant", "content": exchange["assistant"]})
    
    # Add current message
    messages.append({"role": "user", "content": user_message})
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    
    return response.content[0].text


def extract_updates(user_message, assistant_response, memory):
    """Use AI to extract any new info to remember"""
    
    prompt = f"""Based on this conversation, extract any new information to remember.

User said: {user_message}
Assistant said: {assistant_response}

Current memory:
- Health context: {memory['health_context']}
- Goals: {memory['goals']}

Return JSON only:
{{"new_health_info": "any new health details or empty string", "new_goal": "any new goal mentioned or empty string", "action_taken": "any action the user completed or empty string"}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        updates = json.loads(response.content[0].text)
        return updates
    except:
        return {"new_health_info": "", "new_goal": "", "action_taken": ""}


print("Health Coach Agent (with memory)")
print("Type 'quit' to exit")
print("Type 'memory' to see what I remember")
print()

memory = load_memory()

# Check if first time
if not memory["health_context"]:
    print("First time here! Tell me about your health situation:")
    context = input("> ")
    memory["health_context"] = context
    save_memory(memory)
    response = chat(f"Here's my health situation: {context}. What should I focus on first?", memory)
    print(f"\nCoach: {response}\n")
    memory["conversation_history"].append({
        "user": context,
        "assistant": response,
        "timestamp": datetime.now().isoformat()
    })
    save_memory(memory)
else:
    print("Welcome back! Ready to keep building on your progress?")
    print()

while True:
    user_input = input("You: ")
    
    if user_input.lower() == 'quit':
        print("Take care! Your progress is saved.")
        break
    
    if user_input.lower() == 'memory':
        print("\n--- What I Remember ---")
        print(f"Health: {memory['health_context']}")
        print(f"Goals: {memory['goals']}")
        print(f"Actions taken: {memory['actions_taken']}")
        print("------------------------\n")
        continue
    
    response = chat(user_input, memory)
    print(f"\nCoach: {response}\n")
    
    # Save conversation
    memory["conversation_history"].append({
        "user": user_input,
        "assistant": response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Extract and save any new info
    updates = extract_updates(user_input, response, memory)
    if updates.get("new_health_info"):
        memory["health_context"] += f" {updates['new_health_info']}"
    if updates.get("new_goal"):
        memory["goals"].append(updates["new_goal"])
    if updates.get("action_taken"):
        memory["actions_taken"].append(updates["action_taken"])
    
    save_memory(memory)