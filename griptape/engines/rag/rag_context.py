from typing import Optional
from attr import define, field
from griptape.artifacts import TextArtifact


@define(kw_only=True)
class RagContext:
    initial_query: str = field()
    alternative_queries: list[str] = field(factory=list)
    before_query: list[str] = field(factory=list)
    after_query: list[str] = field(factory=list)
    text_chunks: list[TextArtifact] = field(factory=list)
    output: Optional[str] = field(default=None)
