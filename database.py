from datetime import datetime


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

        return True

    def saveContactDetails(self, name, emailID, dbConn):
        my_dict = {"User name": name, "User Email Id": emailID}
        records = dbConn.user_details
        records.insert_one(my_dict)

        return True
