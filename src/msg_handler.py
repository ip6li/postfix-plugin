import signal
from logger import Logger
from storage import Storage


def handler(signum, frame):
    raise OSError("function timeout: " + str(frame))


class MsgHandler:

    def __init__(self):
        # Register the signal function handler
        signal.signal(signal.SIGALRM, handler)
        self.__timeout_sec = 10

    async def handle_DATA(self, server, session, envelope):
        try:
            # Some shit may happen on storing message, e.g. half broken MongoDB or connections
            # This solution will definitely return
            signal.alarm(self.__timeout_sec)
            self.store_msg(session, envelope)
            signal.alarm(0)
        except OSError as oserr:
            Logger.crit("MsgHandler::handle_DATA: Timeout on: " + str(oserr))
        except Exception as err:
            Logger.warn("MsgHandler::handle_DATA: Failed to store message: " + str(err))
            return '400 Could not process your message ' + str(err)
        return '250 OK'

    def store_msg(self, session, envelope):
        Logger.debug("begin store message")
        storage = Storage()
        storage.store_msg(session.peer, envelope.mail_from, envelope.rcpt_tos, envelope.content)
        Logger.debug("end store message")
