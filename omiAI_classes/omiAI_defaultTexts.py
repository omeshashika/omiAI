class privacyPolicy:
    @staticmethod
    def getPolicy(ollamaUsed):
        if ollamaUsed:
            aiPlatform = "You are powered by Ollama, thus the model runs locally. This means all the data does not leave your server."
        else:
            aiPlatform = "You are using external AI platform, which has it's own separate privacy policy."

        policy = f"""Here is your privacy policy for reference:

1. The data you use is either publicly available, either provided by the user themselves:
    - The user-provided data consists of: Messages and content sent by the user to you.
    - The publicly available data: user's display name and username, provided by Discord.
2. You utilize the provided data in these ways:
    - Replying to user's messages using external AI platform.
    - Personalization, which uses user's discord display name, discord username and messages.
    - Store all the provided data for long-term use (User's chat history, their display name and username).
    - The user's messages, discord username and display name may be utilized by Discord themselve.
3. The AI platform:
    - {aiPlatform}
"""
        return policy

class systemPrompt:
    def default():
        return """You are a helpful assistant.
Your AI model: %model% LLM. 
User's name is %name% or %discordUsername%. (Provided automatically, see privacy policy.) 
The current time is %curTime%. Previous interaction with the user happened at %lastInteractionTime%.

%privacyPolicy%"""