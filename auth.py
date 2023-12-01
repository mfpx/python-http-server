import pam
import datetime
import json
import uuid
from time import sleep

class Auth:

    def __check_password(self, password: str | bytes) -> str:
        if isinstance(password, bytes):
            return password.decode("utf-8")
        elif isinstance(password, str):
            return password
        else:
            return ''

    # This will only work if the user running this is able to act as root, actual root privileges not needed
    # This is how PAM is designed to work, overriding this behaviour is not recommended
    # PAM authentication is very situational, as it is system-level, and the user running it must be able to act as root
    # Running this software with root access is generally not recommended, either
    def pam_authenticate(self, username: str | bytes, password: str | bytes) -> bool:
        password = self.__check_password(password)
        return pam.authenticate(username, password, encoding="utf-8", service="login", resetcreds=True)

    def local_authenticate(self, username: str | bytes, password: str | bytes) -> bool:
        password = self.__check_password(password)
        return username == "david" and password == "<PASSWORD>" # tbd

# Three pieces of information known by both server and peer:
# 1. Ticket ID
# 2. Peer IP address
# 3. Data (AES256) encryption key
class NetworkTicketManager:
    class Ticket:
        def __init__(self, login_ip: str, issue_time: datetime.datetime, expiry_time: datetime.datetime) -> None:
            self.login_ip = login_ip
            self.issue_time = issue_time
            self.expiry_time = expiry_time
            self.ticket_id = str(uuid.uuid4())
            self.dict = self.__dict()

        def __dict(self) -> dict:
            return {
                "login_ip": self.login_ip,
                "issue_time": self.issue_time,
                "expiry_time": self.expiry_time,
            }

    def __read_ticket(self, ticket_id: str = None, ip_address: str = None) -> dict:
        if ticket_id is not None:
            with open("cache/tickets.json", "r") as f:
                file_data = f.read()
                return json.loads(file_data)[ticket_id]
        elif ip_address is not None:
            with open("cache/tickets.json", "r") as f:
                file_data = f.read()
                if file_data != '':
                    tickets = json.loads(file_data)
                else:
                    tickets = {}
                for ticket in tickets:
                    if tickets[ticket]["login_ip"] == ip_address:
                        return tickets[ticket]
        else:
            return {}

    def __save_ticket(self, ticket: Ticket) -> None:
        if os.path.isfile("cache/tickets.json"):
            with open("cache/tickets.json", "r") as f:
                file_data = f.read()
                if file_data != '':
                    tickets = json.loads(file_data)
                else:
                    tickets = {}
        else:
            tickets = {}
        with open("cache/tickets.json", "w") as f:
            tickets[ticket.ticket_id] = ticket.dict
            f.write(json.dumps(tickets, indent=4))

    def issue_ticket(self, username: str, login_ip: str) -> Ticket:
        ticket = self.Ticket(
            username,
            login_ip,
            datetime.datetime.now().isoformat(),
            (datetime.datetime.now() + datetime.timedelta(minutes=15)).isoformat()
        )
        self.__save_ticket(ticket)
        return ticket

    def revoke_ticket(self, ticket_id: str) -> None:
        with open("cache/tickets.json", "r") as f:
            file_data = f.read()
            if file_data != '':
                tickets = json.loads(file_data)
            else:
                tickets = {}
        with open("cache/tickets.json", "w") as f:
            tickets.pop(ticket_id)
            f.write(json.dumps(tickets, indent=4))

    def purge_tickets(self) -> None:
        with open("cache/tickets.json", "r") as f:
            file_data = f.read()
            if file_data != '':
                tickets = json.loads(file_data)
            else:
                tickets = {}
        with open("cache/tickets.json", "w") as f:
            for ticket in tickets:
                if tickets[ticket]["expiry_time"] < datetime.datetime.now().isoformat():
                    tickets.pop(ticket)
            f.write(json.dumps(tickets, indent=4))

    def clear_all_tickets(self) -> None:
        with open("cache/tickets.json", "w") as f:
            f.write('')

    def validate_ticket(self, ticket_id: str, ip_address: str) -> bool:
        ticket = self.__read_ticket(ticket_id=ticket_id)
        if ticket == {}:
            return False
        else:
            if ticket["expiry_time"] > datetime.datetime.now().isoformat() and ticket["login_ip"] == ip_address:
                return True
            else:
                self.revoke_ticket(ticket_id)
                return False

ntm = NetworkTicketManager()
ticket = ntm.issue_ticket("192.168.1.1")
print(ntm.validate_ticket(ticket.ticket_id, "192.168.1.1"))
#ntm.clear_all_tickets()

"""
localdb:
{
    "users": {
        "user" {
            "password": "pass",
            "isactive": true,
            "last_login": "2022-01-01T00:00:00Z",
        },
        "user2" {
            "password": "pass2",
            "isactive": false,
            "last_login": "2022-01-02T00:00:00Z",
        }
    },
    "total_users": 2
}
"""