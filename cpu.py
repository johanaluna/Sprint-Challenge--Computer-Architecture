"""CPU functionality."""

import sys
import command
import alu

class CPU:
    """Main CPU class."""

    def __init__(self):
        """
        Construct a new CPU.
        Hint: Add list properties to the `CPU` class to hold 256 bytes of memory 
        and 8 general-purpose registers.
        """
        #DAY 1
        self.ram = [0] * 256            # 256 bytes of memory
        # Register is temporary storage
        self.reg = [0] * 8              # 8 general-purpose registers
        self.reg[7] = 0xF4
        self.pc  = 0                    # set the program counter
        self.create_branchtable()
        # R5 is reserved as the interrupt mask (IM)
        # R6 is reserved as the interrupt status (IS)
        # R7 is reserved as the stack pointer (SP)
        self.sp = 7
        self.fl = 0

    def create_branchtable(self):
        self.branchtable = {}
        
        filename = 'command.py'
        with open(filename) as f:
            for line in f:
                # Ignore comments
                comment_split = line.split("=")
                # Strip out whitespace
                command_name = comment_split[0].strip()
                command_value= comment_split[1].replace("\n","")
                # Ignore blank lines
                name_function = 'handle_'+ command_name
                function = getattr(self, name_function)  
                self.branchtable[int(command_value,2)] = function
    
    """
    ******* RAM READ / WRITE *******
    """

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, MAR, value):
        """
        MAR: memory address register
        """
        self.ram[MAR] = value

    """
    ******* LOADS *******
    """
    def load(self):
        """Load a program into memory."""
        # writes pre-written commands in the program variable to RAM

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            0b10000010, # LDI R0,8
            0b00000000, # Register 0
            0b00001000, # 8 value
            0b01000111, # PRN R0
            0b00000000, # print(8 value)
            0b00000001, # HLT
        ]

        for instruction  in program:
            self.ram_write(address, instruction )
            # self.ram[address] = instruction 
            address += 1
 
    def load_file(self,filename):
        address = 0
        try:
            with open(filename) as f:
                for line in f:
                    # Ignore comments
                    comment_split = line.split("#")
                    # Strip out whitespace
                    num = comment_split[0].strip()
                    # Ignore blank lines
                    if num == '':
                        continue
                    instruction  = int(num,2)
                    self.ram[address] = instruction 
                    address += 1  
        except FileNotFoundError:
            print("File not found")
            sys.exit(2)
    
    """
    ******* Print Out the CPU State *******
    """
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    """
    ******* INSTRUCTIONS *******
    """
    def handle_LDI(self,operand_a,operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3
    def handle_PRN(self,operand_a,operand_b):
        print(self.reg[operand_a])
        self.pc += 2
    def handle_HLT(self,operand_a,operand_b):
        self.running = False
    def handle_LD(self,operand_a,operand_b):
        #Loads registerA with the value at the memory address stored in registerB
        self.reg[operand_a] = self.ram_read(self.reg[operand_b])
        self.pc += 3
    def handle_PRA(self,operand_a,operand_b):
        print(chr(self.reg[operand_a]),end="")
        self.pc += 2

    def handle_CALL(self,operand_a,operand_b):
        # # Set PC to val stored in registers[operand_a]
        # I cannot use Stack here because in the stack I use reg[a]
        self.reg[self.sp] = alu.dec(self.reg[self.sp])
        self.ram_write(self.reg[self.sp], self.pc + 2)
        # set the pc to the value in the register
        # self.handle_PUSH(self.pc+2, operand_b)
        self.pc = self.reg[operand_a]

    def handle_RET(self,operand_a,operand_b):
        """ 
        Return from subroutine
        Pop the value from the top of the stack and store it in the PC.
        """
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] = alu.inc(self.reg[self.sp])
        
        
    def handle_ST(self,operand_a,operand_b):
        """Store value in registerB in the address stored in registerA."""
        self.ram_write(self.reg[operand_a],self.reg[operand_b])
    

    def handle_NOP(self,operand_a,operand_b):
        """No operation. Do nothing for this instruction"""
        pass

    

    """
    ******* COMPARE GREATER/EQUALS/LESS THAN *******
    """
    def handle_JEQ(self,operand_a,operand_b):
        """
        If equal flag is set (true), jump to the address stored in the given register.
        """
        if self.fl & 0b00000001:
            self.handle_JMP(operand_a,operand_b)
        else: 
            self.pc +=2

    def handle_JGE(self,operand_a,operand_b):
        """
        If greater-than flag or equal flag is set (true), 
        jump to the address stored in the given register.
        """
        if self.fl & (0b00000010 | 0b00000001):
            self.handle_JMP(operand_a,operand_b)
        else: 
            self.pc +=2
    
    def handle_JGT(self,operand_a,operand_b):
        """
        If greater-than flag is set (true), jump to the address stored in the given register.
        """
        if self.fl & 0b00000010:
            self.handle_JMP(operand_a,operand_b)
        else: 
            self.pc +=2

    def handle_JLE(self,operand_a,operand_b):
        """
        If less-than flag or equal flag is set (true), jump to the address stored in the given register.
        """
        if self.fl & (0b00000100 | 0b00000001):
            self.handle_JMP(operand_a,operand_b)
        else: 
            self.pc +=2

    def handle_JLT(self,operand_a,operand_b):
        """
        If greater-than flag is set (true), jump to the address stored in the given register.
        """
        if self.fl & 0b00000100:
            self.handle_JMP(operand_a,operand_b)
        else: 
            self.pc +=2
    def handle_JMP(self,operand_a,operand_b):
        """
        Jump to the address stored in the given register.
        Set the PC to the address stored in the given register.
        """
        self.pc = self.reg[operand_a]
    
    def handle_JNE(self,operand_a,operand_b):
        """
        If greater-than flag is set (true), jump to the address stored in the given register.
        """
        
        if self.fl & (0b00000100 | 0b00000010):
            self.handle_JMP(operand_a,operand_b)
        else: 
            self.pc +=2
   
    """
    ******* PUSH / POP *******
    """
    def handle_PUSH(self,operand_a,operand_b):
        """
        Link:
        https://www.youtube.com/watch?v=d-2Peb3pCBg
        Push Data:
        - Decrement the SP
        - Copy the value in the given register to the address pointed to by SP
        """
        # decrement the SP
        
        self.reg[self.sp] = alu.dec(self.reg[self.sp])
        
        # self.ram_write(self.reg[self.sp], self.reg[operand_a])
        self.ram_write(self.reg[self.sp], self.reg[operand_a])
        self.pc += 2
        

    def handle_POP(self,operand_a,operand_b):
        """
        POP Data
        - Copyt the value from the address pointed to by sp 
        - Increase the SP
        """
        # get last value: self.ram_read(self.reg[self.sp])
        self.reg[operand_a] = self.ram_read(self.reg[self.sp])
        # increment the SP
        self.reg[self.sp] = alu.inc(self.reg[self.sp])
        self.pc += 2
        return (self.reg[operand_a])
    
    """
    ******* ALU INSTRUCTIONS *******
    """
    def handle_MUL(self,operand_a,operand_b):
        self.reg[operand_a] = alu.mul(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_ADD(self,operand_a,operand_b):
        self.reg[operand_a] = alu.add(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_SUB(self,operand_a,operand_b):
        self.reg[operand_a] = alu.add(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_AND(self,operand_a,operand_b):
        self.reg[operand_a] = alu._and(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_CMP(self,operand_a,operand_b):
        self.fl = 0b00000000
        self.fl = alu._cmp(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
        return self.fl
    def handle_DEC(self,operand_a,operand_b):
        self.reg[operand_a] = alu.dec(self.reg[operand_a])
        self.pc += 2
    def handle_DIV(self,operand_a,operand_b):
        self.reg[operand_a] = alu.div(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_INC(self,operand_a,operand_b):
        self.reg[operand_a] = alu.inc(self.reg[operand_a])
        self.pc += 2
    def handle_MOD(self,operand_a,operand_b):
        self.reg[operand_a] = alu.mod(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_NOT(self,operand_a,operand_b):
        self.reg[operand_a] = alu._not(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3 
    def handle_OR(self,operand_a,operand_b):
        self.reg[operand_a] = alu._or(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_SHL(self,operand_a,operand_b):
        self.reg[operand_a] = alu.shl(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_SHR(self,operand_a,operand_b):
        self.reg[operand_a] = alu.shr(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3
    def handle_XOR(self,operand_a,operand_b):
        self.reg[operand_a] = alu.xor(self.reg[operand_a],self.reg[operand_b])
        self.pc += 3

    """
    ******* RUN *******
    """    
    def run(self):
        self.running = True
        while self.running:
            # print("pc",self.pc)
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.branchtable[ir](operand_a,operand_b)
            



