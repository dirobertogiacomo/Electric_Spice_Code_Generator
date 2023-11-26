from itertools import product

###### Spice simulation parameters ######

T = '1u' # is the "period" of the waveform
T2 = '0.5u' # is T/2
T_RF = '10p' # is the rise and fall time of the signals. In this case t_rise = t_fall
VDD = '5'

##########################################

# Function to parse the input logic function and replace logical operators
def parse_logic_function(logic_function):
    '''

    logic_function is a string describing the logic function. The singular operations must be enclosed in parenthesis.
    Example: (!A)*B + B*(!A) must be written as ((!A)*B) + (B*(!A))

    '''

    logic_function = logic_function.replace("AND", "&")
    logic_function = logic_function.replace("OR", "|")
    logic_function = logic_function.replace("NOT", "not")
    logic_function = logic_function.replace("!", "not")
    logic_function = logic_function.replace("*", "&")
    logic_function = logic_function.replace("+", "|")
    return logic_function

# Function to generate a truth table
def generate_truth_table(logic_function, input_variables):
    '''

    Generates a truth table form a logic function. 
    logic_function is a string.
    input_variables is a tuple containing the name of the input variables as string.

    Example: input_variables = ["A", "B", "S0"]

    '''
    # Parse the logic function
    parsed_logic_function = parse_logic_function(logic_function)
    
    # Get the number of input variables
    num_variables = len(input_variables)
    
    # Generate all possible input combinations
    input_combinations = list(product([0, 1], repeat=num_variables))
    
    # Evaluate the logic function for each input combination
    truth_table = []
    for inputs in input_combinations:
        input_dict = dict(zip(input_variables, inputs))
        output = eval(parsed_logic_function, input_dict)
        truth_table.append(inputs + (output,))
    
    return truth_table


# find input combinations with output zero and one
def find_input_combinations_with_output_zero_and_one(truth_table):
    ''' 

    Find all the possible input combinations with output zero and one form a truth table. 

    '''
    zero_combinations = []
    one_combinations = []

    # Find input combinations with output 0 and 1
    for row in truth_table:
        if row[-1] == 0:
            zero_combinations.append(row[:-1])
        elif row[-1] == 1:
            one_combinations.append(row[:-1])

    return zero_combinations, one_combinations

# find all possible transitions from zero to one
def find_transitions_from_zero_to_one(zero_combinations, one_combinations):
    '''
    Find all the possible input transitions that give an output transition from zero to one.

    '''

    transition_combinations = []
    
    for zero in range(len(zero_combinations)):
        for one in range(len(one_combinations)):
            transition = []
            transition.append(zero_combinations[zero])
            transition.append(one_combinations[one]) 
            transition_combinations.append(transition)
        
    return transition_combinations

# function to write PWL spice code for simulations 
def PWL_RF_time(zero_combinations, one_combinations, input_variables, output_variable):
    '''
    
    Writes a spice code that generates pwl waveforms for the inputs considering all possible output transitions from zero to one.  
    
    '''

    # number of input variables
    number_input_variables = len(input_variables) 
    # number of input combinations with output = 0
    number_zero_combinations = len(zero_combinations)
    # number of input combinations with output = 1
    number_one_combinations = len(one_combinations)

    # voltage
    V_one = VDD 
    # header
    header = 'PWL('

    delta_t = '+' + T
    t_RF = '+' + T_RF

    # write a txt file
    title = output_variable + ' - PWL Spice code.txt'
    with open(title, 'w') as file:
        file.write('PWL Spice code\n\n')

    for zero in range(number_zero_combinations):

        simulation = ''

        for var in range(number_input_variables):

            # initialising spice code
            spice_code = 'V' + input_variables[var] + ' ' + input_variables[var] + ' GND ' 
            not_spice_code = 'Vnot' + input_variables[var] + ' not' + input_variables[var] + ' GND '
            
            # initialising PWL 
            PWL = header + '0'
            not_PWL = header + '0'

            voltage_in_zero = zero_combinations[zero][var]
            not_voltage_in_zero = zero_combinations[zero][var]

            if voltage_in_zero == 1 : 
                voltage_in_zero = V_one 
                not_voltage_in_zero = '0'
            else: 
                voltage_in_zero = '0'
                not_voltage_in_zero = V_one

            for one in range(number_one_combinations):

                voltage_in_one = one_combinations[one][var]
                not_voltage_in_one = one_combinations[one][var]

                if voltage_in_one == 1:
                    voltage_in_one = V_one
                    not_voltage_in_one = '0'
                else:
                    voltage_in_one = '0'
                    not_voltage_in_one = V_one

                # write 0 transition
                PWL += ' ' + voltage_in_zero + ' ' + delta_t + ' ' + voltage_in_zero + ' ' + t_RF
                # write 1 transition
                PWL += ' ' + voltage_in_one + ' ' + delta_t + ' ' + voltage_in_one + ' ' + t_RF
                #
                not_PWL += ' ' + not_voltage_in_zero + ' ' + delta_t + ' ' + not_voltage_in_zero + ' ' + t_RF
                # write 1 transition
                not_PWL += ' ' + not_voltage_in_one + ' ' + delta_t + ' ' + not_voltage_in_one + ' ' + t_RF
                #
            
            PWL += ' 0)'
            not_PWL += ' 0)'
            # write spice code 
            spice_code += PWL
            simulation += spice_code + '\n'
            not_spice_code += not_PWL
            simulation += not_spice_code + '\n'
        
        with open(title, 'a') as file:
            file.write(simulation)
            file.write('\n')

def measurements(number_one_combinations, output_variable):
    '''
    
    Writes a spice code that measure the rise and fall time and power in output for a logic function.

    number_one_combinations is the number of the input combinations that give an output = 1.
    output_variable is the name of the output variable. Must be a string. 

    '''

    title = output_variable + ' - Measurement Spice code.txt'
    with open(title, 'w') as file:
        file.write('Measure rise and fall time and power\n\n')

    header = '.meas tran'
    CK = 'VCK CK 0 PWL(0 0 +' + T2 + ' '

    i = 1
    j = 1

    for measure in range(number_one_combinations):
        
        # rise and fall time measurement
        t_rise = header + ' t_rise_' + str(measure) + ' TRIG v(' + output_variable + ')=0.1*5 RISE = 1 cross = ' + str(measure + i) + ' TARG v(' + output_variable + ')=0.9*5 RISE = 1 cross = ' + str(measure + i)

        i += 1

        t_fall = header + ' t_fall_' + str(measure) + ' TRIG v(' + output_variable + ')=0.9*5 FALL = 1 cross = ' + str(measure + i) + ' TARG v(' + output_variable + ')=0.1*5 FALL = 1 cross = ' + str(measure + i)

        # power measuremet
        power = header + ' power_'+ str(measure) + ' AVG -v(vdd)*I(Vvdd) TRIG v(CK)= 2.5 RISE = 1 cross = ' + str(j) + ' TARG V(CK)=2.5 FALL = 1 cross = ' + str(j + 2)
        j += 2

        # clock signal for power measurement
        CK = CK + '0 +10p 5 +1u 5 +10p 0 +1u '

        # write txt file
        with open(title, 'a') as file:
            file.write(t_rise + '\n')
            file.write(t_fall + '\n')
            file.write(power + '\n')
    
    CK = CK + '0 +10p 5 +1u 5 +10p 0 +1u 0)'
    with open(title, 'a') as file:
        file.write('*clock signal for power measurement\n')
        file.write(CK + '\n')


def find_propagation_transitions(truth_table,input_variables):
    '''

    Finds all the possible input transitions for the measurement of the propagation time. 

    '''

    number_input_variables = len(input_variables)
    propagation_transitions = []

    for var in range(number_input_variables):
        row = 0
        for row_zero in truth_table:
            if row_zero[var] != row_zero[-1]:
                for row_one in truth_table[row + 1 : ]:
                    if row_one[var] != row_one[-1]:
                        # mask
                        mask = [True]*number_input_variables
                        mask[var] = False

                        comp = []
                        for i in range(number_input_variables):
                            comp.append(row_zero[i]==row_one[i])
                        
                        if mask == comp:
                            propagation_transitions.append([row_zero[:-1], row_one[:-1]])
            row += 1

    return propagation_transitions

def PWL_propagation_time(propagation_transitions, input_variables, output_variable):
    '''
    
    Writes a spice code that generates pwl waveforms for the inputs considering all possible output transitions from zero to one.
    
    '''

    # number of input variables
    number_input_variables = len(input_variables) 
    # number of input combinations with output = 0
    #number_zero_combinations = len(zero_combinations)
    # number of input combinations with output = 1
    #number_one_combinations = len(one_combinations)
    # number of transitions
    number_transitions = len(propagation_transitions)

    # voltage
    V_one = VDD 
    # header
    header = 'PWL('
    header_time = '.meas tran'

    delta_t = '+' + T
    t_RF = '+' + T_RF

    # write a txt file
    title = output_variable + ' - PWL propagation Spice code.txt'
    with open(title, 'w') as file:
        file.write('PWL propagation Spice code\n\n')

    for zero in range(number_transitions):

        simulation = ''

        for var in range(number_input_variables):

            # initialising spice code
            spice_code = 'V' + input_variables[var] + ' ' + input_variables[var] + ' GND ' 
            not_spice_code = 'Vnot' + input_variables[var] + ' not' + input_variables[var] + ' GND '
            
            
            # initialising PWL 
            PWL = header + '0'
            not_PWL = header + '0'

            voltage_in_zero = propagation_transitions[zero][0][var]
            not_voltage_in_zero = propagation_transitions[zero][0][var]

            if voltage_in_zero == 1 : 
                voltage_in_zero = V_one 
                not_voltage_in_zero = '0'
            else: 
                voltage_in_zero = '0'
                not_voltage_in_zero = V_one

            #for one in range(number_transitions):

            voltage_in_one = propagation_transitions[zero][1][var]

            if voltage_in_one == 1:
                voltage_in_one = V_one
                not_voltage_in_one = '0'
            else:
                voltage_in_one = '0'
                not_voltage_in_one = V_one

            # write 0 transition
            PWL += ' ' + voltage_in_zero + ' ' + delta_t + ' ' + voltage_in_zero + ' ' + t_RF
            # write 1 transition
            PWL += ' ' + voltage_in_one + ' ' + delta_t + ' ' + voltage_in_one + ' ' + t_RF
            # write 0 transition
            PWL += ' ' + voltage_in_zero + ' ' + delta_t + ' ' + voltage_in_zero + ' ' + t_RF
            #
            # write 0 transition
            not_PWL += ' ' + not_voltage_in_zero + ' ' + delta_t + ' ' + not_voltage_in_zero + ' ' + t_RF
            # write 1 transition
            not_PWL += ' ' + not_voltage_in_one + ' ' + delta_t + ' ' + not_voltage_in_one + ' ' + t_RF
            # write 0 transition
            not_PWL += ' ' + not_voltage_in_zero + ' ' + delta_t + ' ' + not_voltage_in_zero + ' ' + t_RF
            #
            
            PWL += ' 0)'
            not_PWL += ' 0)'
            # write spice code 
            spice_code += PWL
            simulation += spice_code + '\n'
            not_spice_code += not_PWL
            simulation += not_spice_code + '\n'
        
        with open(title, 'a') as file:
            file.write(simulation)
            file.write('\n')

    # measure
    t_P_HL = header_time + ' tp_inH_outL trig v(X)=2.5 rise=1 targ v(' + output_variable + ')=2.5 fall=1'  
    t_P_LH = header_time + ' tp_inL_outH trig v(X)=2.5 fall=1 targ v(' + output_variable + ')=2.5 rise=1'
    
    with open(title, 'a') as file:
        file.write(t_P_HL + '\n')
        file.write(t_P_LH + '\n')
        file.write('\n')

def print_everything(logic_function, input_variables, output_variable):
    # Generate the truth table
    truth_table = generate_truth_table(logic_function, input_variables)

    # Find input combinations with output 0 and 1
    zero_combinations, one_combinations = find_input_combinations_with_output_zero_and_one(truth_table)

    # find transitions
    transition_combinations = find_transitions_from_zero_to_one(zero_combinations, one_combinations)

    # spice code for simulations
    PWL_RF_time(zero_combinations, one_combinations, input_variables, output_variable)
    measurements(len(one_combinations), output_variable)

    # propagation transitions
    propagation_transitions = find_propagation_transitions(truth_table,input_variables)
    PWL_propagation_time(propagation_transitions, input_variables,output_variable)

    # Display the truth table
    print('Truth table:')
    print(' '.join([f'{var}' for var in input_variables]) + ' | ' + output_variable)
    print("-" * 20)

    for row in truth_table:
        input_str = ' '.join([f'{val}' for val in row[:-1]])
        output_str = row[-1]
        print(f"{input_str} | {output_str}")

    # print transitions
    print("\nTransitions from 0 to 1:")
    for transition in transition_combinations:
        print(f"From: {transition[0]} To: {transition[1]}")

    # simulation time
    sim_time = len(one_combinations)*2 + 2
    print('\nSimulation time:')
    print('.tran ' + str(sim_time) + '*' + T)

    # print propagation transitions
    print("\nPropagation transitions:")
    for transition in propagation_transitions:
        print(f"From: {transition[0]} To: {transition[1]}")

    