"""HTTP server configuration model"""

from pydantic import BaseModel, Extra, Field

# pylint: disable=too-few-public-methods


class HttpServerConfig(BaseModel):
    """HTTP server related settings"""

    interface: str = Field("0.0.0.0", description="Interface address to listen on")

    port: int = Field(8086, description="Port number")

    class Config:
        """Pydantic configuration"""

        extra = Extra.forbid
