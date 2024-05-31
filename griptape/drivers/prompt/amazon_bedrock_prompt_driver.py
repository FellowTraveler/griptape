from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact, TextChunkArtifact
from griptape.utils import import_optional_dependency

from .base_multi_model_prompt_driver import BaseMultiModelPromptDriver

if TYPE_CHECKING:
    import boto3

    from griptape.common import PromptStack


@define
class AmazonBedrockPromptDriver(BaseMultiModelPromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        model_input = self.prompt_model_driver.prompt_stack_to_model_input(prompt_stack)
        payload = {**self.prompt_model_driver.prompt_stack_to_model_params(prompt_stack)}
        if isinstance(model_input, dict):
            payload.update(model_input)

        response = self.bedrock_client.invoke_model(
            modelId=self.model, contentType="application/json", accept="application/json", body=json.dumps(payload)
        )

        response_body = response["body"].read()

        if response_body:
            return self.prompt_model_driver.process_output(response_body)
        else:
            raise Exception("model response is empty")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextChunkArtifact]:
        model_input = self.prompt_model_driver.prompt_stack_to_model_input(prompt_stack)
        payload = {**self.prompt_model_driver.prompt_stack_to_model_params(prompt_stack)}
        if isinstance(model_input, dict):
            payload.update(model_input)

        response = self.bedrock_client.invoke_model_with_response_stream(
            modelId=self.model, contentType="application/json", accept="application/json", body=json.dumps(payload)
        )

        response_body = response["body"]
        if response_body:
            for chunk in response["body"]:
                chunk_bytes = chunk["chunk"]["bytes"]
                yield TextChunkArtifact(value=self.prompt_model_driver.process_output(chunk_bytes).value)
        else:
            raise Exception("model response is empty")
