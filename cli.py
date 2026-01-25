import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a lifestyle medicine health coach focused on helping people with chronic conditions make sustainable behavior changes.

RULES:
1. NEVER ask more than one question per response
2. ALWAYS reference specific details from the user's health context
3. Give concrete, actionable advice immediately — don't just gather information
4. After 2 exchanges, you should have given at least one specific action step
5. Be direct. No fluff. No "that's a great question."
6. Keep responses under 150 words unless explaining something complex
7. Achieve an actionable plan within 4 exchanges
8. Reference scientific evidence when possible

You focus on the 7 pillars:
1. Nutrition
2. Physical activity  
3. Sleep
4. Stress management
5. Social connection
6. Avoiding risky substances
7. Lowering screen time

You are proactive, focused on small actionable steps, and warm but direct."""

conversation_history = []

def chat(user_message):
    conversation_history.append({"role": "user", "content": user_message})
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message


print("Health Coach Agent")
print("Type 'quit' to exit\n")

# Get initial health context
print("First, tell me about your health situation:")
context = input("> ")
response = chat(f"Here's my health context: {context}")
print(f"\nCoach: {response}\n")

# Continue conversation
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        print("Take care!")
        break
    response = chat(user_input)
    print(f"\nCoach: {response}\n")