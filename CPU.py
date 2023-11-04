class MemoryBus:
    """
    Represents a simplified memory bus which allows for reading from and writing to memory addresses.
    """

    def __init__(self):
        """Initializes the memory with an empty dictionary to store data lines."""
        self.data_lines = {}

    def load_data(self, file_path):
        """
        Loads data from a file into the memory bus.

        :param file_path: Path to the file containing memory data in address, value pairs.
        """
        with open(file_path, 'r') as file:
            for line in file:
                address, data = line.strip().split(',')
                self.data_lines[int(address, 2)] = int(data)

    def read(self, address):
        """
        Reads data from a specific memory address.

        :param address: The memory address to read from.
        :return: The data at the specified memory address or None if the address is invalid.
        """
        return self.data_lines.get(address, None)

    def write(self, address, data):
        """
        Writes data to a specific memory address.

        :param address: The memory address to write to.
        :param data: The data to be written.
        """
        self.data_lines[address] = data


class Cache:
    """
    Represents a simplified cache system for a CPU, implementing a direct-mapped cache with an LRU eviction policy.
    """

    def __init__(self, capacity, memory_bus):
        """
        Initializes the cache with a specific capacity and a reference to the memory bus.

        :param capacity: The maximum number of items the cache can hold.
        :param memory_bus: A reference to the memory bus to read data from when cache misses occur.
        """
        self.capacity = capacity
        self.memory_bus = memory_bus
        self.cache_lines = {}

    def read(self, address):
        """
        Reads data from the cache or the underlying memory bus in case of a cache miss.

        :param address: The memory address to read from.
        :return: The data from the cache or memory bus.
        """
        # If the address is in cache, return the data
        if address in self.cache_lines:
            return self.cache_lines[address]
        else:
            # Load the data from memory bus on cache miss
            data = self.memory_bus.read(address)
            if data is not None:
                # Remove the least recently used item if the cache is full
                if len(self.cache_lines) >= self.capacity:
                    least_recently_used = min(self.cache_lines.keys(), key=lambda k: self.cache_lines[k][1])
                    self.cache_lines.pop(least_recently_used)
                # Insert the new item and reset its usage count
                self.cache_lines[address] = (data, 0)
                # Increment the usage count for all items
                for key in self.cache_lines:
                    self.cache_lines[key] = (self.cache_lines[key][0], self.cache_lines[key][1] + 1)
            return data

    def write(self, address, data):
        """
        Writes data to the cache and the memory bus (write-through). Updates the cache if the data is present.

        :param address: The memory address to write to.
        :param data: The data to be written.
        """
        # Write through to memory bus
        self.memory_bus.write(address, data)
        # If the data is in cache, update it and reset its usage count
        if address in self.cache_lines:
            self.cache_lines[address] = (data, 0)
            # Increment the usage count for all other items
            for key in self.cache_lines:
                if key != address:
                    self.cache_lines[key] = (self.cache_lines[key][0], self.cache_lines[key][1] + 1)


class CPU:
    """
    Represents a simplified CPU that can execute a set of instructions and interact with a cache system.
    """

    def __init__(self, cache):
        """
        Initializes the CPU with a reference to a cache and default register values.

        :param cache: A reference to the cache the CPU will interact with.
        """
        self.cache = cache
        self.registers = {'R1': 0, 'R2': 0, 'R3': 0}
        self.PC = 0  # Program Counter
        self.running = True
        self.instructions = []

    def load_instructions(self, file_path):
        """
        Loads instructions from a file into the CPU's instruction set.

        :param file_path: Path to the file containing CPU instructions.
        """
        with open(file_path, 'r') as file:
            self.instructions = [line.strip() for line in file.readlines()]

    def fetch_instruction(self):
        """
        Fetches the next instruction to be executed, based on the current value of the Program Counter (PC).

        :return: The next instruction if available, otherwise None.
        """
        if self.PC < len(self.instructions):
            instruction = self.instructions[self.PC]
            self.PC += 1
            return instruction
        return None

    def execute_instruction(self, instruction):
        """
        Executes a single instruction.

        :param instruction: The instruction to execute, formatted as a string.
        """
        parts = instruction.split(',')
        opcode = parts[0]

        if opcode == "HALT":
            self.running = False
        elif opcode == "ADDI":
            _, dest, src, immediate = parts
            self.registers[dest] = self.registers[src] + int(immediate)
        elif opcode == "ADD":
            _, dest, src1, src2 = parts
            self.registers[dest] = self.registers[src1] + self.registers[src2]
        elif opcode == "J":
            _, address = parts
            self.PC = int(address)
        elif opcode == "CACHE":
            _, address = parts
            data = self.cache.read(int(address))
            print(f"Read from cache: {data}")

    def run(self):
        """
        Executes instructions sequentially until the HALT instruction is encountered or the instruction list is exhausted.
        """
        while self.running:
            instruction = self.fetch_instruction()
            if instruction:
                self.execute_instruction(instruction)
            else:
                break


# Example Usage
memory_bus = MemoryBus()
memory_bus.load_data('data_input.txt')
cache = Cache(capacity=4, memory_bus=memory_bus)  # Assuming a small cache capacity for the example
cpu = CPU(cache=cache)

# Load instructions and run the CPU
cpu.load_instructions('instruction_input.txt')
cpu.run()

# Print cache content
print("Cache state:")
for address, (data, _) in cpu.cache.cache_lines.items():
    print(f"Address: {address:08b}, Data: {data}")

# Print register values
print("Register state:")
print(cpu.registers)
