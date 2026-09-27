import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

load_dotenv()

# =============================
# API CONNECTIONS
# =============================

hindsight_key = os.getenv("HINDSIGHT_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

memory = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=hindsight_key
)

ai = Groq(api_key=groq_key)


# =============================
# SAVE A MEETING
# =============================

def save_meeting(customer, meeting_notes):

    memory_content = f"""
Customer: {customer}

Meeting notes:
{meeting_notes}
"""

    memory.retain(
        bank_id="meeting-memory",
        content=memory_content
    )

    print("\n✅ Meeting saved to Hindsight memory!")


# =============================
# PREPARE FOR A MEETING
# =============================

def prepare_for_meeting(customer):

    print("\n🔎 Searching customer history...")

    memories = memory.recall(
        bank_id="meeting-memory",
        query=customer
    )

    if not memories.results:
        print("\n❌ No memories found for this customer.")
        return

    memory_text = "\n".join(
        item.text for item in memories.results
    )

    print("🧠 Memories found!")
    print("🤖 Preparing your meeting brief...")

    response = ai.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are a Meeting Intelligence Agent.

Your job is to prepare a salesperson for an
upcoming customer meeting.

Analyze the customer's previous meeting memories
and create a concise meeting brief.

Include:

1. Current situation
2. Previous concerns
3. What has been resolved
4. Current priorities
5. Unresolved issues
6. Suggested discussion points

Only use information present in the memories.
Do not invent facts.
"""
            },
            {
                "role": "user",
                "content": f"""
Customer:
{customer}

Customer meeting history:
{memory_text}

Prepare me for my upcoming meeting with this customer.
"""
            }
        ]
    )

    print("\n")
    print("=" * 45)
    print("       🧠 MEETING BRIEF")
    print("=" * 45)
    print(response.choices[0].message.content)
    print("=" * 45)


# =============================
# MAIN PROGRAM
# =============================

print("\n🧠 MEETING INTELLIGENCE AGENT")
print("=" * 35)

while True:

    print("\nWhat would you like to do?")
    print("1. Add a meeting")
    print("2. Prepare for a meeting")
    print("3. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":

        customer = input("\nCustomer name/company: ")
        meeting_notes = input("\nMeeting notes: ")

        save_meeting(customer, meeting_notes)

    elif choice == "2":

        customer = input("\nCustomer name/company: ")

        prepare_for_meeting(customer)

    elif choice == "3":

        print("\nGoodbye! 👋")
        break

    else:

        print("\n❌ Invalid choice. Please choose 1, 2, or 3.")


memory.close()
