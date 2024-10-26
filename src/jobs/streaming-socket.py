import json
import socket
import time
from pathlib import Path
from typing import Generator, Any
import pandas as pd
from contextlib import contextmanager

class DataSender:
    def __init__(self, host: str = '127.0.0.1', port: int = 9999, chunk_size: int = 2):
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

    def read_json_chunks(self, file_path: Path) -> Generator[list, None, None]:
        """Generator to read JSON files in chunks"""
        records = []
        with open(file_path, 'r') as file:
            file.seek(self.last_position)
            for line in file:
                print(f"Reading line: {line}")
                try:
                    records.append(json.loads(line))
                    if len(records) == self.chunk_size:
                        yield records
                        records = []
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON line: {e}")
                    continue
                
            if records:  # Yield remaining records
                yield records

    def send_data(self, data: Any, conn: socket.socket) -> None:
        """Send data over socket connection"""
        try:
            serialized = json.dumps(data, default=self._handle_date).encode('utf-8') + b'\n'
            conn.sendall(serialized)  # Using sendall instead of send
        except (socket.error, TypeError) as e:
            print(f"Error sending data: {e}")
            raise

    @staticmethod
    def _handle_date(obj: Any) -> str:
        """Handle date serialization"""
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")

    def process_file(self, file_path: str) -> None:
        """Main processing function"""
        file_path = Path(file_path)
        print(f"Processing file: {file_path}")
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Listening for connections on {self.host}:{self.port}")
        
        with self.create_server_socket(): # Using context manager
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
                                time.sleep(5)  # Consider making this configurable
                                self.last_position = file_path.tell()
                                
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected.")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                finally:
                    print("Connection closed")

if __name__ == "__main__":
    sender = DataSender()
    sender.process_file("src/datasets/data.json")