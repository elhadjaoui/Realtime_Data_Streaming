from contextlib import contextmanager

@contextmanager
def hello_context_manager():
        print("Entering the context")
        yield "Hello, World!"
        print("Leaving the context")


with hello_context_manager() as hello:
     print(hello)
