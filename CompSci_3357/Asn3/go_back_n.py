import logging
import time
import queue
import threading

class GBN_sender:
    def __init__(self, input_file, window_size, packet_len, nth_packet, send_queue, ack_queue, timeout_interval, logger):
        self.input_file = input_file
        self.window_size = window_size
        self.packet_len = packet_len
        self.nth_packet = nth_packet
        self.send_queue = send_queue
        self.ack_queue = ack_queue
        self.timeout_interval = timeout_interval
        self.logger = logger

        self.base = 0
        self.packets = self.prepare_packets()
        self.acks_list = [False] * len(self.packets)
        self.packet_timers = [0] * len(self.packets)
        self.dropped_list = []
        self.num_sent_packets = 0

        self.logger.info(f"{len(self.packets)} packets created, Window size: {self.window_size}, Packet length: {self.packet_len}, Nth packet to be dropped: {self.nth_packet}, Timeout interval: {self.timeout_interval}")

    def prepare_packets(self):
        try:
            with open(self.input_file, 'r') as f:
                data = f.read()
        except Exception as e:
            self.logger.error(f"Error reading input file: {e}")
            return []

        binary_data = ''.join(format(ord(char), '08b') for char in data)
        packets = []
        seq_num = 0
        data_len = self.packet_len - 16
        for i in range(0, len(binary_data), data_len):
            packet_data = binary_data[i:i + data_len]
            seq_num_bin = format(seq_num, '016b')
            packet = packet_data + seq_num_bin
            packets.append(packet)
            seq_num += 1

        return packets

    def send_packets(self):
        for i in range(self.base, min(self.base + self.window_size, len(self.packets))):
            self.num_sent_packets += 1
            if self.num_sent_packets % self.nth_packet == 0:
                self.dropped_list.append(i)
                self.logger.info(f"packet {i} dropped")
                print(f"sender: packet {i} dropped")
                self.packet_timers[i] = time.time()
            else:
                self.send_queue.put(self.packets[i])
                self.logger.info(f"sending packet {i}")
                print(f"sender: sending packet {i}")
                self.packet_timers[i] = time.time()
    
    def send_next_packet(self):
        self.last_packet = min(self.base + self.window_size, len(self.packets)-1) # a reuqirement
        if self.last_packet == len(self.packets):
            print("NO MORE PACKETS TO SEND")
            return False
        #print(f"sender: send next packet: {self.last_packet}")
        self.packet_timers[self.last_packet] = time.time()
        self.num_sent_packets += 1
        if self.num_sent_packets % self.nth_packet == 0:
            self.dropped_list.append(self.last_packet)
            self.logger.info(f"packet {self.last_packet} dropped")
            print(f"sender: packet {self.last_packet} dropped")
        else:
            self.send_queue.put(self.packets[self.last_packet])
            self.logger.info(f"sending packet {self.last_packet}")
            print(f"sender: sending packet {self.last_packet}")
        self.base += 1

    def check_timers(self):
        for i in range(self.base, min(self.base + self.window_size, len(self.packets))):
            #print(f"HERE IS I: {i}")
            if (time.time() - self.packet_timers[i]) > self.timeout_interval:
                # print(f"sender: packet: {i}, {time.time()} - {self.packet_timers[i]} > {self.timeout_interval}")
                self.logger.info(f"packet {i} timed out")
                print(f"sender: packet {i} timed out")
                self.send_packets()
                return True
        return False

    def receive_acks(self):
        while True:
            ack = self.ack_queue.get()  # Prevent blocking. CHECK ON THIS LATER timeout=self.timeout_interval
                
            if not self.acks_list[ack]:
                self.acks_list[ack] = True
                self.logger.info(f"ack {ack} received")
                print(f"sender: ack {ack} received")
                if ack == len(self.packets) - 1:
                    self.logger.info("Received ack for last packet.")
                    print(f"Received ack for last packet.")
                    self.base += 1 # Stop the run function
                    break
                self.send_next_packet()  # Send the next packet in the sliding window
            else:
                self.logger.info(f"ack {ack} received, Ignoring")  # Log ignored acknowledgment
              
    def run(self):
        self.send_packets()
        ack_thread = threading.Thread(target=self.receive_acks)
        ack_thread.start()
        
        while self.base < len(self.packets):
            self.check_timers()
        
        print("sender: sending None")
        self.send_queue.put(None)  # Notify receiver that transmission is complete
        ack_thread.join()  # Wait for the acknowledgment thread to finish


class GBN_receiver:
    def __init__(self, output_file, send_queue, ack_queue, logger):
        self.output_file = output_file
        self.send_queue = send_queue
        self.ack_queue = ack_queue
        self.logger = logger
        self.packet_list = []
        self.expected_seq_num = 0

    def process_packet(self, packet):
        seq_num = int(packet[-16:], 2)
        print(f"receiver: Processing packet {seq_num}, expected {self.expected_seq_num}")
        self.logger.info(f"Processing packet {seq_num}")
        if seq_num == self.expected_seq_num:
            self.packet_list.append(packet[:-16])
            self.logger.info(f"packet {seq_num} received")
            self.ack_queue.put(seq_num)
            self.expected_seq_num += 1
            return True
        else:
            self.logger.info(f"packet {seq_num} received out of order")
            self.ack_queue.put(self.expected_seq_num - 1)  # Acknowledge the last in-order packet
            return False

    def write_to_file(self):
        with open(self.output_file, 'w') as f:
            data = ''.join(self.packet_list)
            chars = [chr(int(data[i:i + 8], 2)) for i in range(0, len(data), 8)]
            f.write(''.join(chars))

    def run(self):
        while True:
            packet = self.send_queue.get()
            if packet is None:
                self.logger.info("Received termination signal.")
                print("receiver: got None, terminating")
                break
            self.process_packet(packet)

        self.write_to_file()
