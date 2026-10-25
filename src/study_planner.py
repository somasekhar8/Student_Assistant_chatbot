
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(override=True)

STUDY_PLAN_PROMPT = """
You are a senior academic advisor.
Create a simple, highly structured study plan for a student.

Student Profile:
- Subject: {subject}
- Current Knowledge Level: {level}
- Daily Available Hours: {hours} hours/day
- Preparation Timeframe: {days} days

Output Format Requirements:

1. Overview & Goal:
A brief overview sentence setting expectations.

2. Day-by-Day Schedule:
Provide a day-by-day table/list showing:
- Day Number
- Target Topic
- Recommended Practice Activity

3. Key Revision Strategy:
Provide 2-3 specific tips tailored to the student's level.

Keep the schedule realistic based on available hours.
"""


def generate_study_plan(
    subject: str,
    level: str,
    hours: float,
    days: int
) -> str:

    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if not groq_key and not google_key:
        return "Error: No API keys configured."

    prompt = ChatPromptTemplate.from_template(
        STUDY_PLAN_PROMPT
    )

    inputs = {
        "subject": subject,
        "level": level,
        "hours": hours,
        "days": days
    }

    # Initialize only configured providers
    providers = []

    if groq_key:
        try:
            groq_llm = ChatGroq(
                model="openai/gpt-oss-12",
                temperature=0.3,
                groq_api_key=groq_key,
                timeout=30,
                max_retries=1
            )

            providers.append(("Groq", groq_llm))

        except Exception as e:
            print(f"Groq initialization failed: {e}")

    if google_key:
        try:
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-3.8-flash",
                temperature=0.3,
                google_api_key=google_key,
                timeout=30,
                max_retries=1
            )

            providers.append(("Gemini", gemini_llm))

        except Exception as e:
            print(f"Gemini initialization failed: {e}")

    if not providers:
        return "Error: No LLM provider could be initialized."

    # Execute Groq first, Gemini second
    for provider_name, llm in providers:

        try:
            print(f"Trying {provider_name}...")

            chain = prompt | llm | StrOutputParser()

            response = chain.invoke(inputs)

            if not response or not response.strip():
                raise ValueError("Empty response received")

            print(f"Successfully generated using {provider_name}")

            return response

        except Exception as e:

            print(f"{provider_name} failed: {e}")

            print("Trying next available provider...")

            continue

    return (
        "Failed to generate study plan. "
        "All configured LLM providers failed. "
        "Check terminal logs for details."
    )
