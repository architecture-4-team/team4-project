from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    uuid: str
    contact_id: str
    email: str
    password: str
    firstname: str
    lastname: str
    ip: str
    status: str
    summary: str
    created_at: datetime
    updated_at: datetime
