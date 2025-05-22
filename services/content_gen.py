import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

async def generate_daily_posts(topic: str, method: str = "one time", days: int = None):
    if not method:
        method = "one time"

    posts = []

    if method.lower() == "one time":
        prompt = f"""
You are a professional content creator and researcher with cutting-edge knowledge about the topic: '{topic}'.

        Your task is to create a detailed, educational, and engaging LinkedIn post.

        🎯 Output Format:
        - Start with an attention-grabbing question (avoid exaggeration).
        - Clearly introduce the topic and explain why it's important.
        - Describe how it benefits people or solves real-world problems.
        - Highlight how professionals or industries are using it today.
        - Include links to relevant, authoritative learning resources.
        - Use relatable and trending hashtags relevant to the topic.
        - Avoid using **bold** syntax as LinkedIn does not support markdown.
        - Add the hashtag `#AutopostIn`.

        The tone should be crisp, informative, and LinkedIn-friendly.
"""
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": prompt}]
        )
        text = response.output_text
        posts.append({"day": 1, "content": text})

    elif method.lower() == "day series" and days:
        for day in range(1, days + 1):
            prompt = f"""
        You are designing a multi-day educational series on LinkedIn to help users learn '{topic}'.

        For Day {day}/{days}:
        - Write a post titled: "Day {day}/{days} of Learning {topic}"
        - Introduce a relevant subtopic or lesson.
        - Provide clear, actionable explanation.
        - Add a link or resource to learn more.
        - Avoid using **bold** syntax as LinkedIn does not support markdown.
        - Include `#AutopostIn` and other topic-relevant hashtags.
"""
            response = client.responses.create(
                model="gpt-4o",
                input=[{"role": "user", "content": prompt}]
            )
            text = response.output_text
            posts.append({"day": day, "content": text})

    elif method.lower() == "roadmap":
        prompt = f"""
        You are an AI educator writing a full learning roadmap on the topic: '{topic}'.

        Build a detailed step-by-step plan covering:
        - Stages of learning (e.g. beginner → intermediate → advanced)
        - Each topic with 1–2 line explanation
        - Real-world project suggestions per stage
        - Free or trusted resources (e.g. books, MOOCs, blogs)
        - Common mistakes and tips for success
        - Avoid using **bold** syntax as LinkedIn does not support markdown.
        - Include `#AutopostIn` and 3 topic-specific hashtags

        Keep it structured, exhaustive, and readable.
"""
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": prompt}]
        )
        posts.append({"day": 1, "content": response.output_text})

    elif method.lower() == "daily":
        for day in range(1, 6):
            prompt = f"""You are an AI-powered LinkedIn post generator creating daily content on the topic: '{topic}'.(Day {day}/5)

        Each post should:
        - Pick one sub-concept, recent innovation, or trending news in the domain.
        - Explain it in a beginner-friendly and insightful way.
        - Include a resource (article, course, video, etc.) to explore more.
        - Avoid repeating previous posts – make each one unique.
        - Use real-world applications or implications.
        - Avoid using **bold** syntax as LinkedIn does not support markdown.
        - Include relevant hashtags + `#AutopostIn`."""
            response = client.responses.create(
                model="gpt-4o",
                input=[{"role": "user", "content": prompt}]
            )
            posts.append({"day": day, "content": response.output_text})

    elif method.lower() == "weekly":
        for week in range(1, 5):
            prompt = f"""You are a weekly thought leader on LinkedIn post for Week {week} for the topic: '{topic}'.

        For this week's post:
        - Choose a medium-depth concept, news event, or trend in the field.
        - Write a compelling explanation with practical insight or industry usage.
        - Include 1–2 useful resources (article, paper, or tool) for further exploration.
        - Make it valuable enough that people want to comment or share.
        - Avoid using **bold** syntax as LinkedIn does not support markdown.
        - Include trending and topic-specific hashtags + `#AutopostIn`.
        """
            response = client.responses.create(
                model="gpt-4o",
                input=[{"role": "user", "content": prompt}]
            )
            posts.append({"week": week, "content": response.output_text})

    return {
        "topic": topic,
        "method": method,
        "posts": posts
    }
