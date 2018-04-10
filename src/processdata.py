import argparse
from datetime import datetime

from typing import *

from session import Session
import os
from argparse import ArgumentParser

os.chdir(os.getcwd())


class ProcessData(object):
    """
    This object handles the processing of data and consists of essential data structures

    LRU data structures such as queue (session_queue) and map (ip_session_data) is used to process the log data
    Session_queue contains ip_adressess
    ip_session_data contains ip_address as key and value as Session object
    """
    ip_session_data = None  # type: Dict[str, Session]
    session_queue = None  # type: List[str]
    data_field_index = None  # type: Dict[str, int]

    def __init__(self):

        self.ip_session_data = dict()
        self.session_queue = list()

        # Initialize filenames, path for I/O
        self.input_path = str()
        self.input_filename = str()
        self.timeout_file = str()
        self.output_path = str()
        self.output_filename = str()

        # Initialize file pointer attributes
        self.in_file = None
        self.out_file = None

        # Session live period
        self.TIMEOUT = 0

        # correspondence between data fields and index in the file
        self.data_field_index = dict()

        # essential header in consideration
        self.header_names = [
            "ip",
            "date",
            "time",
            "cik",
            "accession",
            "extention"]

        # Used to keep constant track of previously processed batch
        # It enables processing one or more batch(es) at a time
        # one batch is defined as all sessions started at nth second
        self.last_batch_time = str()

    def set_filename(self, arguments):
        """

        :param args: contains command line arguments for file I/O parameters
        :return: null
        """
        self.input_filename = arguments.input
        self.output_filename = arguments.output
        self.timeout_file = arguments.timeout
        self.input_path = arguments.input_path
        self.output_path = arguments.output_path

        pass

    def read_file_data(self):
        """
        This function reads contents of a file to obtain session expiry period
        and the log data file

        For the log data file, headers are processed and the data is processed line by line to populate the data
        structures
        :return:
        """

        with open(self.input_path + self.timeout_file, "r") as fp:
            self.TIMEOUT = int(fp.readline())

        self.in_file = open(self.input_path + self.input_filename, "r")
        self.out_file = open(self.output_path + self.output_filename, "w")

        # process the header names
        header = self.in_file.readline().strip("\n")
        if header:
            self.create_data_field_index(header)
        else:
            print("Header not present")
            exit()

        # set the first datetime as the last_batch_time
        curr_line = self.in_file.readline().strip("\n")
        if curr_line:
            self.set_last_batch_time(curr_line)
        else:
            print("No session data")
            exit()

        # Process each line
        while curr_line:
            self.process_session(curr_line)
            curr_line = self.in_file.readline().strip("\n")

        # Process remaining data in the data structures to the file
        self.remove_remainder_session()

        self.in_file.close()
        self.out_file.close()

        pass

    def set_last_batch_time(self, line):
        """
        extract datetime from line to set last_batch_time variable
        :param line: one line from log data
        :return: null
        """
        data_fields = line.split(",")
        date = str()
        time = str()
        try:
            date = data_fields[self.data_field_index["date"]]
            time = data_fields[self.data_field_index["time"]]

        except ValueError:
            print("Data input corrupted")

        if not date or not time:
            raise Exception("Date/Time fields are empty")
        self.last_batch_time = get_datetime(date, time)
        pass

    def create_data_field_index(self, header):
        """
        Identify the index of respective data fields from the header line of the log data file

        :param header: first lien of log data
        :return: null
        """
        all_header_names = header.split(",")

        for one_header in self.header_names:
            try:
                self.data_field_index[one_header] = all_header_names.index(
                    one_header)
            except ValueError:
                print("Value not present ", one_header)
                exit()
        pass

    def process_session(self, curr_line):
        """
        Segregate function argument log line into sub elements to initialize a session object
        Compare the current log datatime with last_batch_time to decide to process output the previous expired sessions
        Check if the user session is active/present to update/create a new session object

        :param curr_line: one line of log data
        :return: null
        """
        curr_data_fields = curr_line.split(",")
        curr_ip = str()
        curr_date = str()
        curr_time = str(0)
        try:
            curr_ip = curr_data_fields[self.data_field_index["ip"]]
            curr_date = curr_data_fields[self.data_field_index["date"]]
            curr_time = curr_data_fields[self.data_field_index["time"]]
        except ValueError:
            print("Data input corrupted")

        if not curr_ip or  not curr_date or  not curr_time:
            raise Exception("Date/Time/IP fields are empty")
        curr_datetime = get_datetime(curr_date, curr_time)  # type: datetime

        if ((curr_datetime - self.last_batch_time).total_seconds()) >= self.TIMEOUT + 1:
            self.remove_batch_session(curr_datetime)

        if curr_ip in self.ip_session_data:
            self.update_session(curr_ip, curr_datetime)
        else:
            self.create_session(curr_ip, curr_datetime)

        pass

    def create_session(self, ip, date_time):
        """
        Creates session object and add to session_queue and ip_session_data map
        :param ip: ip_address of a user
        :param date_time: datetime of timestamp of the web request
        :return: null
        """
        new_session = Session(ip, date_time)
        self.session_queue.append(ip)

        self.ip_session_data[ip] = new_session
        pass

    def update_session(self, ip, date_time):
        """
        Retrieve the session object from the ip_session_data map and update the last_session_date
        Remove the entry of ip from the queue. and add to the end of queue
        Update map with the Session object

        :param ip: ip_address of session
        :param date_time: current datetime of the session from the log data
        :return: null
        """
        curr_session = self.ip_session_data[ip]
        self.session_queue.remove(ip)

        curr_session.set_last_session_time(date_time)
        curr_session.increment_doc()
        self.ip_session_data[ip] = curr_session

        self.session_queue.append(ip)
        pass

    def remove_batch_session(self, curr_date_time):
        """
        All the sessions which are expired (calculated by comparing the datetime difference, curr_date_time by TIMEOUT
        variable) are removed from the data structures and written to the output file

        :param curr_date_time: current datetime being analyzed
        :return: null
        """
        while self.session_queue:

            past_ip = self.session_queue[0]
            past_session = self.ip_session_data[past_ip]
            past_datetime = past_session.get_last_session_time()

            seconds_difference = (
                curr_date_time -
                past_datetime).total_seconds()
            if seconds_difference < self.TIMEOUT + 1:
                self.last_batch_time = past_datetime
                break

            self.write_to_file(past_session)
            self.session_queue.remove(past_ip)
            self.ip_session_data.pop(past_ip)

        pass

    def write_to_file(self, curr_session):
        """
        Obtain formatted output string from session object and write to the output file

        :param curr_session: Session object
        :return:
        """
        line = curr_session.get_write_str()
        self.out_file.write(line)
        pass

    def remove_remainder_session(self):
        """
        Sort the remiander session data present in ip_session_data first by first_session_time and
        later by last_session_time

        :return: null
        """
        remainder_ip = sorted(
            self.ip_session_data,
            key=lambda x: (
                self.ip_session_data[x].first_session_time,
                self.ip_session_data[x].last_session_time))

        for ip in remainder_ip:
            past_session = self.ip_session_data[ip]
            self.write_to_file(past_session)

        pass


def get_datetime(date, time):
    # type: (str, str) -> datetime
    """

    :param date: (str) date of format yyyy-mm-dd
    :param time: (str) time of format hh24:mm:ss
    :return: (datetime) combined date and time to initialize datetime object
    """
    return datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S")


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()  # type: ArgumentParser
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--timeout", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument(
        "--input_path",
        type=str,
        required=False,
        default="../input/")
    parser.add_argument(
        "--output_path",
        type=str,
        required=False,
        default="../output/")
    arguments = parser.parse_args()

    # process log data
    pd = ProcessData()
    pd.set_filename(arguments)
    pd.read_file_data()
