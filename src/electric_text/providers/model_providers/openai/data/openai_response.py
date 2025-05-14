from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


@dataclass
class TokenUsage:
    """Token usage information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_tokens_details: Dict[str, Any]
    output_tokens_details: Dict[str, Any]


@dataclass
class ContentItem:
    """A single content item in the message."""
    type: str
    annotations: List[Any]
    text: str


@dataclass
class Message:
    """A message in the response."""
    id: str
    type: str
    status: str
    content: List[ContentItem]
    role: str


@dataclass
class TextFormat:
    """Text format configuration."""
    type: str
    name: str
    schema: Dict[str, Any]
    strict: bool
    description: Optional[str] = None


@dataclass
class Reasoning:
    """Reasoning information."""
    effort: Optional[Any]
    summary: Optional[Any]


@dataclass
class OpenAIResponse:
    """Complete OpenAI API response."""
    id: str
    object: str
    created_at: datetime
    status: str
    error: Optional[Any]
    incomplete_details: Optional[Any]
    instructions: Optional[Any]
    max_output_tokens: Optional[int]
    model: str
    output: List[Message]
    parallel_tool_calls: bool
    previous_response_id: Optional[str]
    reasoning: Reasoning
    service_tier: str
    store: bool
    temperature: float
    text: Dict[str, TextFormat]
    tool_choice: str
    tools: List[Any]
    top_p: float
    truncation: str
    usage: TokenUsage
    user: Optional[Any]
    metadata: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenAIResponse':
        """Create an OpenAIResponse instance from a dictionary."""
        # Create a copy of the data to avoid mutating the input
        processed_data = {}
        
        # Copy all fields from the input data
        for key, value in data.items():
            processed_data[key] = value
        
        # Process text format
        if 'text' in processed_data and 'format' in processed_data['text']:
            text_format = processed_data['text']['format']
            processed_data['text'] = dict(processed_data['text'])  # Create a copy
            
            # Handle the case when format only has 'type' and not the required fields
            if isinstance(text_format, dict) and 'type' in text_format:
                if 'name' not in text_format:
                    text_format['name'] = 'default'
                if 'schema' not in text_format:
                    text_format['schema'] = {}
                if 'strict' not in text_format:
                    text_format['strict'] = False
            
            processed_data['text']['format'] = TextFormat(**text_format)
        
        # Process messages
        if 'output' in processed_data:
            processed_data['output'] = [
                Message(
                    id=msg['id'],
                    type=msg['type'],
                    status=msg['status'],
                    content=[
                        ContentItem(**content)
                        for content in msg['content']
                    ],
                    role=msg['role']
                )
                for msg in processed_data['output']
            ]
        
        # Process reasoning
        if 'reasoning' in processed_data:
            processed_data['reasoning'] = Reasoning(**processed_data['reasoning'])
        
        # Process usage
        if 'usage' in processed_data:
            processed_data['usage'] = TokenUsage(**processed_data['usage'])
        
        return cls(**processed_data)

    def get_content_text(self) -> Optional[str]:
        """Get the text content from the first message's first content item."""
        if not self.output:
            return None
        
        message = self.output[0]
        if not message.content:
            return None
        
        content_item = message.content[0]
        return content_item.text 