import re

# perform the local value numbering optimization
def LVN(program):

    # returns 3 items:
    
    # 1. a new program (list of classier instructions)
    # with the LVN optimization applied

    # 2. a list of new variables required (e.g. numbered virtual
    # registers and program variables)

    # 3. a number with how many instructions were replaced
    num_table = {} #vn_table
    register_table = {} #reg_table
    vn_reg_table = {} #vn_to_reg
    opt_ir = [] #new_ir
    new_var = []
    val_num = 1 #value_number
    temp_var_used = 0 #temp_var_count
    saved_instr = 0 #saved_instr_count DELETE ALL THIS BEFORE PUSHING

    binary_op_re = re.compile('(vr\d+) = (addi|addf|muli|mulf|subi|subf|divi|divf)\((vr\d+), ?(vr\d+)\);') #match vrX = op(vrX,vrX);
    unary_op_re = re.compile("(vr\d+) = (vr_int2float|vr_float2int)\((vr\d+)\);") #match vrX = op(vrX)
    convert_re = re.compile('(vr\d+) = (int2vr|float2vr)\(([\d.]+)\);') #match vrX = op(int/float)
    #label_branch_re = re.compile('(branch|beq|return|label[\d]+:|vr\d+:|[^=]*:).*') #match labelX: or branch(labelX) or return or beq[vrX, vrX, labelX]
    
    for line in program:
        strip_line = line.strip() #stripping whitespace
        
        #bin_match = binary_op_re.match(strip_line)
        if binary_op_re.match(strip_line):
            #print("Found Binary Op\n")
            dest, op, arg1, arg2 = bin_op_re.match(strip_line).groups()
            #dest, arg1, and arg2 are vr's. op is op

            num1 = register_table.setdefault(arg1,value_number)
            if arg1 not in register_table:
                value_number += 1
            num2 = register_table.setdefault(arg2,value_member)
            if arg2 not in register_table:
                value_number += 1
        

            if op in ['addi', 'multi', 'addf', 'multf']:
                if num1 < num2:
                    key = (op, num1,num2)
                else:
                    key = (op,num1,num2)
            else:
                key = (op,num1,num2)
            #normalize communicative operators' operands into the same order (smaller operand first)
        
            if key in num_table:
                saved_instr += 1
                existing_reg = vn_reg_table[num_table[key]]
                opt_ir.append(f'{dest}_{val_num} = {existing_reg};')
                register_table[dest] = num_table[key]
                new_var.append(f'{dest}_{val_num}')
            else:
                num_table[key] = val_num
                register_table[dest] = val_num
                vn_reg_table[val_num] = dest
                opt_ir.append(strip_line)
                val_num += 1

        elif unary_op_re.match(line):
            #print('Found Unary Op\n')
            dest, op, arg = unary_op_re.match(line).groups()
            #dest and arg are vr's. op is op

            num = register_table.setdefault(arg,val_num)
            if arg not in reg_table:
                val_num += 1
            
            key = (op, num)

            if key in num_table:
                saved_instr += 1
                existing_reg = vn_reg_table[num_table[key]]
                opt_ir.append(f'{dest}_{val_num} = {existing_reg};')
                register_table[dest] = num_table[key]
                new_var.append(f'{dest}_{val_num}')
            else:
                num_table[key] = val_num
                register_table[dest] = val_num
                vn_reg_table[val_num] = dest
                opt_ir.append(line)
                val_num += 1
        elif convert_re.match(strip_line):
            #print('Found convert op\n')
            #convert_match = convert_re.match(strip_line)
            if convert_re.match(strip_line):
                dest, op, val = convert_re.match(strip_line).groups()
                key = (op,val)
                if key in num_table:
                    saved_instr += 1
                    existing_reg = vn_reg_table[num_table[key]]
                    opt_ir.append(f'{dest}_{val_num} = {existing_reg};')
                    register_table[dest] = num_table[key]
                    new_var.append(f'{dest}_{val_num}')
                else:
                    num_table[key] = val_num
                    register_table[dest] = val_num
                    vn_reg_table[val_num] = dest
                    opt_ir.append(strip_line)
                    val_num += 1
        else:
            opt_ir.append(strip_line)

    return opt_ir,new_var,saved_instr
