OPTAB = {
    'ADD': {'opcode': '18', 'format': 3},
    'ADDF': {'opcode': '58', 'format': 3},
    'ADDR': {'opcode': '90', 'format': 2},
    'AND': {'opcode': '40', 'format': 3},
    'CLEAR': {'opcode': 'B4', 'format': 2},
    'COMP': {'opcode': '28', 'format': 3},
    'COMPF': {'opcode': '88', 'format': 3},
    'COMPR': {'opcode': 'A0', 'format': 2},
    'DIV': {'opcode': '24', 'format': 3},
    'DIVF': {'opcode': '64', 'format': 3},
    'DIVR': {'opcode': '9C', 'format': 2},
    'FIX': {'opcode': 'C4', 'format': 1},
    'FLOAT': {'opcode': 'C0', 'format': 1},
    'HIO': {'opcode': 'F4', 'format': 1},
    'J': {'opcode': '3C', 'format': 3},
    'JEQ': {'opcode': '30', 'format': 3},
    'JGT': {'opcode': '34', 'format': 3},
    'JLT': {'opcode': '38', 'format': 3},
    'JSUB': {'opcode': '48', 'format': 3},
    'LDA': {'opcode': '00', 'format': 3},
    'LDB': {'opcode': '68', 'format': 3},
    'LDCH': {'opcode': '50', 'format': 3},
    'LDF': {'opcode': '70', 'format': 3},
    'LDL': {'opcode': '08', 'format': 3},
    'LDS': {'opcode': '6C', 'format': 3},
    'LDT': {'opcode': '74', 'format': 3},
    'LDX': {'opcode': '04', 'format': 3},
    'LPS': {'opcode': 'D0', 'format': 3},
    'MUL': {'opcode': '20', 'format': 3},
    'MULF': {'opcode': '60', 'format': 3},
    'MULR': {'opcode': '98', 'format': 2},
    'NORM': {'opcode': 'C8', 'format': 1},
    'OR': {'opcode': '44', 'format': 3},
    'RD': {'opcode': 'D8', 'format': 3},
    'RMO': {'opcode': 'AC', 'format': 2},
    'RSUB': {'opcode': '4C', 'format': 3},
    'SHIFTL': {'opcode': 'A4', 'format': 2},
    'SHIFTR': {'opcode': 'A8', 'format': 2},
    'SIO': {'opcode': 'F0', 'format': 1},
    'SSK': {'opcode': 'EC', 'format': 3},
    'STA': {'opcode': '0C', 'format': 3},
    'STB': {'opcode': '78', 'format': 3},
    'STCH': {'opcode': '54', 'format': 3},
    'STF': {'opcode': '80', 'format': 3},
    'STI': {'opcode': 'D4', 'format': 3},
    'STL': {'opcode': '14', 'format': 3},
    'STS': {'opcode': '7C', 'format': 3},
    'STSW': {'opcode': 'E8', 'format': 3},
    'STT': {'opcode': '84', 'format': 3},
    'STX': {'opcode': '10', 'format': 3},
    'SUB': {'opcode': '1C', 'format': 3},
    'SUBF': {'opcode': '5C', 'format': 3},
    'SUBR': {'opcode': '94', 'format': 2},
    'SVC': {'opcode': 'B0', 'format': 2},
    'TD': {'opcode': 'E0', 'format': 3},
    'TIO': {'opcode': 'F8', 'format': 1},
    'TIX': {'opcode': '2C', 'format': 3},
    'TIXR': {'opcode': 'B8', 'format': 2},
    'WD': {'opcode': 'DC', 'format': 3}
}


def parse_line(line):
    if line.startswith('.'):  # Comment line
        return None, None, None
    parts = line.split()
    if len(parts) == 1:
        return None, parts[0], None
    elif len(parts) == 2:
        return None, parts[0], parts[1]
    elif len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return None, None, None

def pass_one(lines):
    LOCCTR = '0000'
    intermediate = []
    symtab = {}
    for i, line in enumerate(lines):
        if line.strip() == '' or line.strip().startswith('.'):
            continue
        label, opcode, operand = parse_line(line.strip())
        if label:
            symtab[label] = LOCCTR
        if opcode:
            if opcode.upper() == 'START':
                LOCCTR = operand
                intermediate.append((LOCCTR, line.strip()))
                continue
            elif opcode.upper() in OPTAB:
                LOCCTR = hex(int(LOCCTR, 16) + OPTAB[opcode.upper()]['format'])[2:].upper().zfill(4)
            elif opcode.upper() == 'BYTE':
                if operand.startswith('C\''):
                    LOCCTR = hex(int(LOCCTR, 16) + len(operand[2:-1]))[2:].upper().zfill(4)
                elif operand.startswith('X\''):
                    LOCCTR = hex(int(LOCCTR, 16) + (len(operand[2:-1]) + 1) // 2)[2:].upper().zfill(4)
            elif opcode.upper() == 'WORD':
                LOCCTR = hex(int(LOCCTR, 16) + 3)[2:].upper().zfill(4)
            elif opcode.upper() == 'RESW':
                LOCCTR = hex(int(LOCCTR, 16) + 3 * int(operand))[2:].upper().zfill(4)
            elif opcode.upper() == 'RESB':
                LOCCTR = hex(int(LOCCTR, 16) + int(operand))[2:].upper().zfill(4)
            intermediate.append((LOCCTR, line.strip()))
    return intermediate, symtab

def pass_two(intermediate, symtab):
    object_codes = []
    for LOCCTR, line in intermediate:
        _, opcode, operand = parse_line(line)
        if opcode.upper() in OPTAB:
            code = OPTAB[opcode.upper()]['opcode']
            # Handle operands which may include labels or constants
            if operand:
                # Check for indexed addressing mode
                if ',' in operand:
                    operand, indexing = operand.split(',')
                    operand = operand.strip()
                    indexing = indexing.strip()
                    if indexing == 'X':
                        # Indexed addressing mode requires adding the 'x' bit in the object code
                        address = symtab.get(operand, '0000')
                        address = int(address, 16) | 0x8000  # Set x bit as 1
                        code += format(address, '05X')[:5]  # Ensure we only take 5 hex digits
                    else:
                        raise ValueError("Invalid indexing mode or register")
                else:
                    # Direct addressing mode
                    address = symtab.get(operand, '0000')
                    code += format(int(address, 16), '06X')
            object_codes.append(f"{LOCCTR} {code}")
        else:
            # Handling for directives or undefined opcodes
            if opcode.upper() not in ['START', 'END', 'BYTE', 'WORD', 'RESW', 'RESB']:
                object_codes.append(f"{LOCCTR} No object code for {opcode}")
            else:
                object_codes.append(f"{LOCCTR} No object code needed for {opcode}")
    return object_codes

def main():
    with open('input.asm', 'r') as file:
        lines = file.readlines()
    
    intermediate, symtab = pass_one(lines)
    object_codes = pass_two(intermediate, symtab)

    with open('intermediate.txt', 'w') as int_file:
        for entry in intermediate:
            int_file.write(f"{entry[0]} {entry[1]}\n")
    
    with open('object_code.txt', 'w') as obj_file:
        for code in object_codes:
            obj_file.write(f"{code}\n")

    with open('symbol_table.txt', 'w') as sym_file:
        for sym, addr in symtab.items():
            sym_file.write(f"{sym}: {addr}\n")

if __name__ == "__main__":
    main()

def assemble_code(code):
    try:
        lines = code.splitlines()
        intermediate, symtab = pass_one(lines)
        object_codes = pass_two(intermediate, symtab)
        
        # Writing to temporary files to be able to send them as a response
        intermediate_path = 'temp_intermediate.txt'
        object_code_path = 'temp_object_code.txt'
        
        with open(intermediate_path, 'w') as int_file:
            for entry in intermediate:
                int_file.write(f"{entry[0]} {entry[1]}\n")
        
        with open(object_code_path, 'w') as obj_file:
            for code in object_codes:
                obj_file.write(f"{code}\n")
        
        return object_code_path, None
    except Exception as e:
        return None, str(e)


def assemble(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        intermediate, symtab = pass_one(lines)
        object_codes = pass_two(intermediate, symtab)
        
        intermediate_path = file_path.replace('.asm', '_intermediate.txt')
        object_code_path = file_path.replace('.asm', '_object_code.txt')
        
        with open(intermediate_path, 'w') as int_file:
            for entry in intermediate:
                int_file.write(f"{entry[0]} {entry[1]}\n")
        
        with open(object_code_path, 'w') as obj_file:
            for code in object_codes:
                obj_file.write(f"{code}\n")
        
        return object_code_path, None
    except Exception as e:
        return None, str(e)
