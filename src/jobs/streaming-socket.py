import json
import socket
import time
from contextlib import contextmanager
import pandas as pd

class DataSender:
    def __init__(self, host: str = 'spark-master', port: int = 9999, chunk_size: int = 2):
        self.host = host
        self.port = port
        self.chunk_size = chunk_size
        self.socket = None
        self.last_position = 0

    @contextmanager
    def create_server_socket(self):
        """Context manager for socket handling"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            yield self.socket
        finally:
            if self.socket:
                self.socket.close()

    def read_json_chunks(self, file_path: str):
        """Generator to read JSON files in chunks"""
        records = []
        with open(file_path, 'r') as file:
            file.seek(self.last_position)  # Start reading from the last position
            
            while True:
                line = file.readline()  #read each line
                if not line:
                    break
                
                print(f"Reading line: {line}")
                try:
                    records.append(json.loads(line))
                    if len(records) == self.chunk_size:
                        self.last_position = file.tell()  # Update last position
                        yield records
                        records = []
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON line: {e}")
                    continue

            if records:  # Yield remaining records
                self.last_position = file.tell()  # Update last position after reading remaining records
                yield records

    def send_data(self, data, conn: socket.socket) -> None:
        """Send data over socket connection"""
        try:
            serialized = json.dumps(data, default=self._handle_date).encode('utf-8') + b'\n'
            conn.sendall(serialized)
        except (socket.error, TypeError) as e:
            print(f"Error sending data: {e}")
            raise

    @staticmethod
    def _handle_date(obj) -> str:
        """Handle date serialization"""
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")

    def process_file(self, file_path: str) -> None:
        """Main processing function"""
        print(f"Processing file: {file_path}")
        
        try:
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Listening for connections on {self.host}:{self.port}")
        
        with self.create_server_socket():
            while True:
                try:
                    conn, addr = self.socket.accept()
                    print(f"Connection from {addr}")
                    
                    with conn:
                        for records in self.read_json_chunks(file_path):
                            chunk_df = pd.DataFrame(records)
                            print(chunk_df)
                            
                            for record in chunk_df.to_dict(orient='records'):
                                self.send_data(record, conn)
                                time.sleep(2)  # Consider making this configurable
                                
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected.")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                finally:
                    print("Connection closed")

if __name__ == "__main__":
    sender = DataSender(host='localhost', port=9999, chunk_size=2)
    sender.process_file("src/datasets/yelp_academic_dataset_review.json")
