# OpenAI Plugins

The plugin currently features ChatGPT and Batch API agents.

To install the plugin, run the following command:

```bash
pip install flytekitplugins-openai
```

## ChatGPT

The ChatGPT plugin allows you to run ChatGPT tasks within the Flyte workflow without requiring any code changes.

```python
from flytekit import task, workflow
from flytekitplugins.openai import ChatGPTTask, ChatGPTConfig

chatgpt_small_job = ChatGPTTask(
    name="chatgpt gpt-3.5-turbo",
    openai_organization="org-NayNG68kGnVXMJ8Ak4PMgQv7",
    chatgpt_config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
    },
)

chatgpt_big_job = ChatGPTTask(
    name="chatgpt gpt-4",
    openai_organization="org-NayNG68kGnVXMJ8Ak4PMgQv7",
    chatgpt_config={
            "model": "gpt-4",
            "temperature": 0.7,
    },
)


@workflow
def wf(message: str) -> str:
    message = chatgpt_small_job(message=message)
    message = chatgpt_big_job(message=message)
    return message


if __name__ == "__main__":
    print(wf(message="hi"))
```
