import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('databaseManager.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Log:
    def __init__(self):
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")

    def saveConversations(self, session_id, user_query, parameters, bot_message, intent, dbConn):
        my_dict = {"sessionID": session_id, "User Query": user_query, "User Intent": intent, "Parameters": parameters,
                   "Bot": bot_message, "Date": str(self.date) + "/" + str(self.current_time)}
        records = dbConn.chat_record
        records.insert_one(my_dict)
        logger.info("Conversation records save SUCCESSFULLY")
        return True

    def saveContactDetails(self, name, emailID, dbConn):
        my_dict = {"User name": name, "User Email Id": emailID}
        records = dbConn.user_details
        records.insert_one(my_dict)
        logger.info("Contact details save SUCCESSFULLY")
        return True
