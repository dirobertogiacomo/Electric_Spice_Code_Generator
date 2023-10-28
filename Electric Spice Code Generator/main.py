import functions

ns0 = "((S1 AND S0) OR (S0 AND (NOT A)) OR ((NOT S1) AND (NOT S0) AND A))"
ns1 = "((NOT S1) AND A) OR (S1  AND (NOT A))"
Y = "(S0 AND ( ((NOT S1) AND (NOT A)) OR (S1 AND A)) )"

# Input logic function and variables
logic_function = Y
input_variables = ["A", "S0", "S1"]
output_variable = 'Y'

functions.print_everything(logic_function, input_variables, output_variable)