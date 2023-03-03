import json
import socket
import time
import numpy as np

EXECUTOR_IP = 'localhost'
EXECUTOR_PORT = 8080


class Connection:
    """This class handles the connection with a microscope executor"""

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.connection = None

    def connect(self, timeout=40):
        """Creates a TCP socket meant to send commands to the RT-ip_address
        """
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.settimeout(timeout)
            self.connection.connect((self.ip_address, self.port))
        except socket.error as err:
            print("Failed to establish connection.")
            raise err

    def is_connected(self):
        """Return whether or not our connection is active."""
        # TODO: Implement some kind of ping to check if we can actually send data
        return self.connection is not None

    def echo(self):
        # TODO: define an echo call for debugging
        raise NotImplementedError

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def run_command(self, command: str, args=(), msg_length=20):
        """This method sends to the RT-ip_address a Json command message in the following way
        - three numbers representing the command
        - if there are arguments to send:
            - the length of the messages to follow = msglength
            - the amount of messages to follow
        - receives acknowledgement of reception receiving an error code

        args is a list of strings containing the arguments associated.

        Return a Dictionary with the error description:
        Error Status, Error code and Error Description
        """
        # Transform args into a list of strings of msg_length chars
        send_args = []
        for arg in args:
            if type(arg) is float:
                raise Exception('Arguments to send cannot be floats')
            if type(arg) == str and len(arg) <= msg_length:
                send_args.append(arg.rjust(msg_length, '0'))
            elif type(arg) == int and len(str(arg)) <= msg_length:
                send_args.append(str(arg).rjust(msg_length, '0'))
            else:
                send_args.append(str(arg).rjust(msg_length, '0'))

        # Create a dictionary to be flattened and sent as json string
        message_cluster = {'command': command,
                           'message_len': msg_length,
                           'nr_of_messages': len(send_args)
                           }

        try:
            # Send the actual command
            self.connection.send(json.dumps(message_cluster).encode())
            # self.connection.send(b'\r\n')
        except socket.error as msg:
            print('Send message_cluster failed.\n', msg)

        try:
            # Send the actual messages buffer
            buf = str('').join(send_args).encode()
            self.connection.sendall(buf)
        except socket.error as msg:
            print('Send buffer failed.\n', msg)

        # try:
        #     # receive confirmation error
        #     # errorLength = int(self.connection.recv(4).decode())
        #     # if errorLength:
        #     try:
        #         datagram = self.connection.recv(1024)
        #         error = json.loads(datagram)
        #         if error['status']:
        #             print(f'There has been an FPGA error: {error}')
        #     except:
        #         print('We received a TCP error when confirming command.')
        #         # errorLength.append(self.connection.recv(4096))
        #         # datagram = self.connection.recv(4096)
        #
        except socket.error as msg:  # Send failed
            print('Receiving error.\n', msg)
        return

    def abort(self):
        """Sends abort experiment command to FPGA
        """
        self.run_command("abort")

    def reset(self):
        """Restarts the executor
        """
        self.run_command("reset")

    def set_nr_reps(self, nr_reps: int):
        """Updates the number of repetitions to execute.
        """
        nr_reps = [nr_reps]
        msg_length = len(str(nr_reps))

        self.run_command("set_nr_reps", nr_reps, msg_length=msg_length)

    def set_tables(self, digitals_table, analogue_tables, msg_length=20, digitalsBitDepth=32, analoguesBitDepth=16):
        """Sends through TCP the digitals and analogue tables to the RT-ip_address.

        Analogues lists must be ordered form 0 onward and without gaps. That is,
        (0), (0,1), (0,1,2) or (0,1,2,3). If a table is missing a dummy table must be introduced
        msg_length is an int indicating the length of every digital table element as a decimal string
        """
        # Convert the digitals numpy table into a list of messages for the TCP
        digitals_list = []

        for t, value in digitals_table:  # TODO: Change this into a more efficient code
            digitals_value = int(np.binary_repr(t, 32) + np.binary_repr(value, 32), 2)
            digitals_list.append(digitals_value)

        self.run_command('set_digitals', digitals_list, msg_length)

        # Send Analogues
        for analogue_table, analogue_channel in enumerate(analogue_tables):

            # Convert the analogues numpy table into a list of messages for the TCP
            analogue_list = []

            for t, value in analogue_table:  # TODO: optimize this
                analogue_value = int(np.binary_repr(t, 32) + np.binary_repr(value, 32), 2)
                analogue_list.append(analogue_value)

            self.run_command(f"set_analogues_{analogue_channel}", analogue_list, msg_length)

    def set_indexes(self, index_set, digitals_start_index, digitals_stop_index, analogues_start_indexes, analogues_stop_indexes,
                    msg_length=20):
        """Writes to the FPGA the start and stop indexes of the actionTables that
        have to be run on an experiment. Actually, multiple 'indexSets' can be used
        (up to 16) to be used in combined experiments.

        index_set -- the index_set where the indexes are to be sent to. integer from 0 to 15
        digitals_start_index -- the start point of the digitals table. Included in
        the execution of the experiment. integer up to u32bit
        digitals_stop_index -- the stop point of the digitals table. NOT included in
        the execution of the experiment. integer up to u32bit
        analogues_start_indexes -- iterable containing the start points of the analogues tables.
        Included in the execution or the experiment. list or tuple of integers up to u32bit
        analogues_stop_indexes -- iterable containing the stop points of the analogues tables.
        NOT included in the execution or the experiment. list or tuple of integers up to u32bit
        msg_length is an int indicating the length of every element as a decimal string
        """
        # TODO: Validate the value of index_set is between 0 and 15
        # TODO: Validate that analogues lists are the same length

        # Merge everything in a single list to send. Note that we interlace the
        # analogue indexes (start, stop, start, stop,...) so in the future we can
        # put an arbitrary number.
        send_list = [index_set, digitals_start_index, digitals_stop_index]

        analogues_interleaved = [x for t in zip(analogues_start_indexes, analogues_stop_indexes) for x in t]

        for index in analogues_interleaved:
            send_list.append(index)

        # send indexes.
        self.run_command('set_indexes', send_list, msg_length)

    def prepare_actions(self, actions, nb_reps):
        """Sends a actions table to the cRIO and programs the execution of a number of repetitions.
        It does not trigger the execution"""
        # We upload the tables to the cRIO
        self.set_tables(digitals_table=actions[1], analogue_tables=actions[2])

        # Now we can send the Indexes.
        # The indexes will tell the FPGA where the table starts and ends.
        # This allows for more flexibility in the future, as we can store more than
        # one experiment per table and just execute different parts of it.
        # Memory addresses on the FPGA are 0 based. We, however, use 1 based indexing so we
        # can initialize certain values on the 0 address of the FPGA, such as a safe state we can
        # securely rely on.
        digitals_start_index = 1
        digitals_stop_index = len(actions[1])
        analogues_start_indexes = [1 for x in actions[2]]
        analogues_stop_indexes = [len(x) for x in actions[2]]
        self.set_indexes(index_set=0,
                         digitals_start_index=digitals_start_index,
                         digitals_stop_index=digitals_stop_index,
                         analogues_start_indexes=analogues_start_indexes,
                         analogues_stop_indexes=analogues_stop_indexes,
                         msg_length=20)

        # We initialize the profile. That is tell the cRIO how many repetitions to produce and the interval.
        # TODO: Because the generic Executor is adding a last element in the table we put a 0 here. Change this
        self.init_profile(nb_reps=nb_reps, rep_duration=0)

        return True

    def run_experiment(self):
        self.run_command("run_experiment")

    def is_idle(self):
        """Returns True if experiment is running and False if idle
        """
        raise NotImplementedError

    def is_aborted(self):
        """Returns True if FPGA is aborted (in practice interlocked) and False if idle
        """
        raise NotImplementedError

    def flushFIFOs(self):
        """Flushes the FIFOs of the FPGA.
        """
        # TODO: This has to be done on the executor
        raise NotImplementedError

    def read_analogue(self, line):
        """Returns the current output value of the analog line in native units
        line is an integer corresponding to the requested analog on the FPGA
        as entered in the analog config files.
        """
        raise NotImplementedError

    def move_absolute(self, channel, value_ADU, msg_length=20):
        """Changes an channel output to the specified analogueValue value

        analogueValue is taken as a raw 16 or 32bit value
        channel is an integer corresponding to the analogue in the FPGA as specified in the config files
        msg_length is an int indicating the max length of the analogue as a decimal string
        """
        analogue = [channel, int(value_ADU)]
        self.run_command('write_analogue', analogue, msg_length)
        while self.read_analogue(analogue[0]) != analogue[1]:
            time.sleep(0.01)
        return

    def write_analogue_delta(self, value, channel):
        """Changes an channel output to the specified analogueValue delta-value

        value is taken as a raw 16bit value
        channel is an integer corresponding to the analogue in the FPGA as specified in the config files
        """
        raise NotImplementedError

    def write_digitals(self, digital_value, msg_length=20):
        """Write a specific value to the ensemble of the digitals through a 32bit
        integer digital_value.
        msg_length is an int indicating the length of the digital_value as a decimal string
        """
        digital_value = [digital_value]
        self.run_command('write_digitals', digital_value, msg_length)

    def read_digital(self, channel=None):
        """Get the value of the current Digitals outputs as a 32bit integer.
        If channel is specified, a 0 or 1 is returned.
        """
        raise NotImplementedError

    def init_profile(self, nb_reps, rep_duration=0, msg_length=20):
        """Prepare the FPGA to run the loaded profile.
        Send a certain number of parameters:
        numberReps and a rep_duration

        numberReps -- the number of repetitions to run
        rep_duration -- the time interval between repetitions
        msg_length -- int indicating the length of numberReps and rep_duration as decimal strings
        """
        self.run_command('init_profile', [nb_reps, rep_duration], msg_length)

    def run_sequence(self, time_digital_sequence, digitals_bit_depth=32, msg_length=20):
        """Runs a small sequence of digital outputs at determined times"""
        send_list = []
        for t, d in time_digital_sequence:
            # binarize and concatenate time and digital value
            value = np.binary_repr(t, 32) + np.binary_repr(d, digitals_bit_depth)
            value = int(value, 2)
            send_list.append(value)

        self.run_command('run_sequence', send_list, msg_length)

