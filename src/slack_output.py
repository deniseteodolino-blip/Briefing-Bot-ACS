import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
SLACK_USER_ID = os.getenv('SLACK_USER_ID') or os.getenv('SLACK_CHANNEL')


def create_private_canvas(message: str, title: str = "Briefing ACS") -> dict:
    """
    Create a private message to the user's DM for review.
    After review, user can copy and post to the channel.
    """
    try:
        channel = SLACK_USER_ID

        result = slack_client.chat_postMessage(
            channel=channel,
            text=f"*{title}*\n\n_VERIFIQUE E COPIE PARA ENVIAR AO CSI_",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{title}*\n\n_VERIFIQUE E COPIE PARA ENVIAR AO CSI_"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "_Revise a mensagem acima. Para enviar ao CSI, copie e cole no canal #suporte-cs-investimentos._"
                        }
                    ]
                }
            ]
        )

        print(f"Mensagem enviada para sua DM: {result['ts']}")
        return {
            "ok": True,
            "channel": result['channel'],
            "ts": result['ts'],
            "message": message
        }

    except SlackApiError as e:
        print(f"Erro ao enviar DM: {e}")
        return {
            "ok": False,
            "error": str(e),
            "message": message
        }


def post_to_channel(channel: str, message: str, thread_ts: str = None) -> dict:
    """
    Post message directly to a channel (requires bot permissions).

    Args:
        channel: Channel ID or name (e.g., #suporte-cs-investimentos)
        message: Message text
        thread_ts: Optional thread timestamp for replies
    """
    try:
        result = slack_client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=thread_ts
        )

        return {
            "ok": True,
            "channel": result['channel'],
            "ts": result['ts']
        }

    except SlackApiError as e:
        return {
            "ok": False,
            "error": str(e)
        }


def format_message_for_copy(message: str) -> str:
    """Format message for easy copy-paste to Slack."""
    # Remove markdown formatting if any
    formatted = message.replace('*', '').replace('_', '')
    return formatted