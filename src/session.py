

class Session(object):
    """
    This object corresponds to a user uniquely defined by ip_address

    Data members:
    ip_address (str) : unique to identify a user
    first_session_time (datetime) : timestamp for the first request
    last_session_time (datetime) : timestamp for the last request
    num_doc (int) : number of documents accessed

    """

    def __init__(self, ip, first_session_time):
        self.ip_address = ip
        self.first_session_time = first_session_time
        self.last_session_time = first_session_time
        self.num_doc = 1

    def set_last_session_time(self, last_session_time):
        """
        :param last_session_time: timestamp for current session
        :return: null
        """
        self.last_session_time = last_session_time
        pass

    def get_last_session_time(self):
        """

        :return: last_session_time: timestamp for last session
                    requested by user_session
        """
        return self.last_session_time

    def get_ip(self):
        """

        :return: ip_address of the user_session
        """
        return self.ip_address

    def increment_doc(self):
        """
        Increments count of document by 1
        :return:null
        """
        self.num_doc += 1
        pass

    def get_write_str(self):
        """

        :return: expected output format for one expired session
        """
        return self.ip_address + "," + \
            self.first_session_time.strftime("%Y-%m-%d %H:%M:%S") + "," + \
            self.last_session_time.strftime("%Y-%m-%d %H:%M:%S") + "," + \
            str(int((self.last_session_time -
                     self.first_session_time).total_seconds() + 1)) +\
            "," + str(self.num_doc) + "\n"
