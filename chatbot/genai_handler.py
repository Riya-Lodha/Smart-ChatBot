import os
import asyncio
from typing import Optional
from openai import AzureOpenAI
from openai import AuthenticationError, RateLimitError, APIConnectionError


class GenAIHandler:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint="https://openaipocinref.openai.azure.com/"
        )
        self.conversation_history= {}
        self.max_history = 10

    async def generate_response_stream(self, text: str, session_id: Optional[str] = "default"):
        try:
            prev_response = self.conversation_history.get(session_id, "")
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
            
            if prev_response:
                messages.insert(1, {"role": "assistant", "content": prev_response})

            response_stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                stream=True
            )

            full_response = ""
            try:
                for chunk in response_stream:
                    if chunk and chunk.choices and len(chunk.choices) > 0:
                        if hasattr(chunk.choices[0], 'delta'):
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content:
                                content = delta.content
                                full_response += content
                                yield content
                                await asyncio.sleep(0.01)

            except Exception as stream_error:
                yield f"Error processing stream: {str(stream_error)}"
                return

            if full_response:
                self.conversation_history[session_id] = full_response

                if len(self.conversation_history) > self.max_history:
                    oldest_session = next(iter(self.conversation_history))
                    del self.conversation_history[oldest_session]
            
        except AuthenticationError:
            yield "Error: Authentication failed. Please check API key."
        except RateLimitError:
            yield "Error: Rate limit exceeded. Please try again later."
        except APIConnectionError:
            yield "Error: Unable to connect to AI services."
        except Exception as e:
            yield f"Error: {str(e)}"

    def clear_history(self, session_id: str = "default"):
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

    def get_history(self, session_id: str = "default") -> str:
        return self.conversation_history.get(session_id, "")