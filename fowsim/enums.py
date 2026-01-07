from enum import Enum


class TournamentPermissions(Enum):
    CAN_READ = "can_read"
    CAN_WRITE = "can_write"
    CAN_DELETE = "can_delete"
