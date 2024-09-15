#Python Brainfuck interpreter

import sys
import os


argv = sys.argv[1::]


# intrpreter parameters

# wheather to use the jit to optimize
jit = False

# path to the brainfuck source file
file = None

# the maximum index in array
array_max = 30_000

# the minimum index in array
array_min = 0

# wheather to wrap from array_max to array_min and vice versa
# if active out_of_bound_crash is ignored
wrap_array = True

# ends the program if something trys to go out of the array bound -> array_max < cursor < array_min
# does not work with wrap_array active
out_of_bound_crash = False

# the max value a cell can have 8-bit: 2^8 = 255; 16-bit: 2^16 = 65535; ...
# this value can be chosen arbitrarily
max_value = 255

# the min value a cell can have. For u8, u16, ... its Zero 
# this value can be chosen arbitrarily
# a value < 0 may cause unforseen problems in comination with the . command
min_value = 0

# wheater to go from max_value to min_value and vice versa
# if active value_too_big_crash is ignored
wrap_value = True

# ends the program if something trys to go out of the value bound -> max_value < *p < min_value
# does not work with wrap_array active
value_too_big_crash = False

# debug mode
debug = False


# parses the commandline arguments

help_page = ["-h", "--h", "-help", "--help"]
jit_cli = ["-c", "--c", "-comp", "--comp", "-jit", "--jit"]
arraymax = ["-arrmax", "--arrmax", "-arraymax", "--arraymax"]
arraymin = ["-arrmin", "--arrmin", "-arraymin", "--arraymin"]
wraparray = ["-warpa", "--warpa", "-warparray", "--warparray"]
boundcrash = ["-crashb", "--crashb", "-crashbounds", "--crashbounds"]
maxvalue = ["-valmax", "--valmax", "-valuemax", "--valuemax"]
minvalue = ["-valmin", "--valmin", "-valuemin", "--valuemin"]
wrapvalue = ["-warpv", "--warpv", "-warpvalue", "--warpvalue"]
toobigcrash = ["-crasht", "--crasht", "-crashtoobig", "--crashtoobig"]
debug_cli = ["-debug", "--debug"]


# helper methode to print information when using the --help or -h command
def print_help():
    print(", ".join(help_page) + ": The page you are seeing right now")
    print(", ".join(jit_cli) + ": Toggles the jit compiler. This may cause uninteded behaviour. Default: " + str(jit))
    print(" [max], ".join(arraymax) + ": The Right bound of the array. Default: " + str(array_max))
    print(" [min], ".join(arraymin) + ": The Left bound of the array. Default: " + str(array_min))
    print(", ".join(wraparray) + ": Toggle wheather to wrap around the array. Default: " + str(wrap_array))
    print(", ".join(boundcrash) + ": Toggle wheater to crash on an array out of bounds. Default: " + str(out_of_bound_crash))
    print(" [max], ".join(maxvalue) + ": The Heighest value of a cell. Default: " + str(max_value))
    print(" [min], ".join(minvalue) + ": The Lowest value of a cell. Default: " + str(min_value))
    print(", ".join(wrapvalue) + ": Wheather to simulate integer overflow. Default: " + str(wrap_value))
    print(", ".join(toobigcrash) + ": Wheater to crash on an integer overflow. Default: " + str(value_too_big_crash))
    print(", ".join(debug_cli) + ": Enable debug mode. Default: " + str(debug))


# -h to access the help page
if any(i in argv for i in help_page):
    print_help()
    # logicly the should be no need to run something if you need help
    # so the programm kills its self
    sys.exit()

# toggles the jit
# activate the jit compiler
if any(i in argv for i in jit_cli):
    jit = not jit

# to set the max array index
if any(i in argv for i in arraymax):
    l = [argv.index(i) if i in argv else 9999 for i in arraymax]
    index = min(l) + 1
    if index < len(argv):
        array_max = int(argv[index])

# to set the min array index
if any(i in argv for i in arraymin):
    l = [argv.index(i) if i in argv else 9999 for i in arraymin]
    index = min(l) + 1
    if index < len(argv):
        array_min = int(argv[index])

# toggles wrap_array
# deactivates wrap_array to wrap from start to end and vice versa
if any(i in argv for i in wraparray):
    wrap_array = not wrap_array

# toggles out_of_bound_crash
# activates out_of_bound_crash to crash to programm if the array goes out of bounds
if any(i in argv for i in boundcrash):
    out_of_bound_crash = not out_of_bound_crash

# to set the max value for each cell
if any(i in argv for i in maxvalue):
    l = [argv.index(i) if i in argv else 9999 for i in maxvalue]
    index = min(l) + 1
    if index < len(argv):
        max_value = int(argv[index])

# to set the min value for each cell
if any(i in argv for i in minvalue):
    l = [argv.index(i) if i in argv else 9999 for i in minvalue]
    index = min(l) + 1
    if index < len(argv):
        min_value = int(argv[index])

# toggles wrap_value
# deactivates wrap_value to wrap from the highest to the lowest value and vice versa
if any(i in argv for i in wrapvalue):
    wrap_value = not wrap_value

# toggles value_too_big_crash
# activates value_too_big_crash to crash to programm if the value goes out of bounds
if any(i in argv for i in boundcrash):
    value_too_big_crash = not value_too_big_crash

# toggles debug
if any(i in argv for i in debug_cli):
    debug = not debug

# assums that the file path is the first argument
if os.path.isfile(argv[0]):
    file = argv[0]


# debuging
if debug:
    print("Jit: " + str(jit))
    print("array_max: " + str(array_max))
    print("array_min: " + str(array_min))
    print("wrap_array: "+ str(wrap_array))
    print("out_of_bound_crash: " + str(out_of_bound_crash))
    print("max_value: " + str(max_value))
    print("min_value: " + str(min_value))
    print("wrap_value: " + str(wrap_value))
    print("value_too_big_crash: " + str(value_too_big_crash))


#=====================================================#
#                                                     #
#                  Programm Logic                     #
#                                                     #
#=====================================================#

# error if no file path was found
if file == None:
    print("no file provided")
    sys.exit()



# runtime variable setup for interpreter and jit

# the input made at the beginning to simulate an input stream
inp = ""
# cursor to keep track where in the string we are
inp_cur = 0

# array substitute which supports negative indexes and blank indexes (which aren't used at the time)
# the first element is either 0 or the number x closest to zero matching array_min <= x <= array_max
dic =  {min(array_max ,max(0, array_min)): 0}
# cursor to keep track where in the data we are
cursor = min(array_max ,max(0, array_min))

# an array to keep track of the loops we are in
# loops[x] the cursor to the [ that started the loop
# loops[0] is the first loop we entered in the current loop nesting
# loops[-1] is the most recent loop entered
loops = []

# the file content wihtout newlines
content = None

# the value a new field is initialised with
# the value is either 0 or the number x clossetst to matching min_value <= x <= max_value
init_value = min(max_value ,max(0, min_value))

# reads the source files content
with open(file) as f:
    content = f.read().replace('\n', '')

# if for somereason the file coudnt be read an error is thrown TODO better error catching
if content == None:
    print("Error reading File " + file)
    sys.exit()


#compile down for faster interpreter use
if jit:
    # a dict to convert the chars to numbers to directly index of an array instead of a dict lookup
    char_map = {"<": 0, ">": 1, "+": 2, "-": 3, "[": 4, "]": 5, ",": 6, ".": 7}
    # same but backwards -> numbers to char commands
    char_map_back = {0: "<", 1: ">", 2: "+", 3: "-", 4: "[", 5: "]", 6: ",", 7: "."}
    # a string containing all the allowed characters compiled down from the char_map
    allowed_chars = "".join(list(char_map.keys())) #"<>+-[],." 

    # a list with all the commands in numeric form as an array for faster access and comput time
    compiled_cont = []
    # programm counter like cursor (to know where you are in the programm)
    compiled_cont_cur = 0
    # how many commands there are
    compiled_cont_len = None

    # wheather you need to ask the user for an input (if the program doesnt require one the user doent need to enter on)
    need_input = False

    # converts the souce read from the file to the binary code used here
    for s in content:
        if s in allowed_chars:
            # checks if there is a user input required
            if s == ",":
                need_input = True
            compiled_cont.append(char_map[s])

    # asks user for input if required
    if need_input:
        inp = input("Please Enter all Character the Program may need\n")

    # determines the number of commands to use for fourther optimizations
    compiled_cont_len = len(compiled_cont)

    # a variable to save wheather the "compiler" optimized something to repeat the steps to posibly catch further optimizations
    changed = True 

    # optimization loop
    while changed:
        changed = False

        #empty loop optimization (removes empty loops)
        compiled_cont_cur = 0
        while compiled_cont_cur < compiled_cont_len:
            if compiled_cont_cur + 1 < compiled_cont_len and compiled_cont[compiled_cont_cur] == char_map["["] and compiled_cont[compiled_cont_cur + 1] == char_map["]"]:
                del compiled_cont[compiled_cont_cur:compiled_cont_cur + 2]
                compiled_cont_len -= 2
                changed = True
                continue
            
            compiled_cont_cur += 1
        
        # TODO better optimizations

        

    # determines the number of commands again to ensure accuracy
    compiled_cont_len = len(compiled_cont)
    
    #print("".join([str(x) for x in compiled_cont]))

    # implements the < command for jit
    def left():
        global dic
        global cursor
        global compiled_cont_cur

        if cursor <= array_min:
            if wrap_array:
                cursor = array_max
            elif out_of_bound_crash:
                print("array out of bound at char " + compiled_cont_cur)
        else:
            cursor -= 1
        if cursor not in dic:
            dic[cursor] = init_value

    # implements the > command for jit
    def right():
        global dic
        global cursor
        global compiled_cont_cur

        if cursor >= array_max:
            if wrap_array:
                cursor = array_min
            elif out_of_bound_crash:
                print("array out of bound at char " + compiled_cont_cur)
                sys.exit()
        else:
            cursor += 1
        if cursor not in dic:
            dic[cursor] = init_value

    # implements the + command for jit
    def plus():
        global dic
        global cursor
        global compiled_cont_cur

        if dic[cursor] >= max_value:
            if wrap_array:
                dic[cursor] = min_value
            elif value_too_big_crash:
                print("value to big at char " + compiled_cont_cur)
                sys.exit()
        else:
            dic[cursor] += 1

    # implements the - command for jit
    def minus():
        global dic
        global cursor
        global compiled_cont_cur

        if dic[cursor] <= min_value:
            if wrap_array:
                dic[cursor] = max_value
            elif value_too_big_crash:
                print("value to small at char " + compiled_cont_cur)
                sys.exit()
        else:
            dic[cursor] -= 1

    # implements the [ command for jit
    def loop_s():
        global dic
        global cursor
        global loops
        global compiled_cont
        global compiled_cont_cur
        global compiled_cont_len
        
        if dic[cursor] != 0:
            loops.append(compiled_cont_cur)
        
        else:
            n_loop = -1 #to count how deep you are in the loop nesting
            while compiled_cont_cur < compiled_cont_len and (compiled_cont[compiled_cont_cur] != char_map["]"] or n_loop > 0):
                if compiled_cont[compiled_cont_cur] == char_map["["]:
                    n_loop += 1
                elif compiled_cont[compiled_cont_cur] == char_map["]"]:
                    n_loop -= 1
                compiled_cont_cur += 1

    # implements the ] command for jit
    def loop_e():
        global dic
        global cursor
        global loops
        global compiled_cont_cur

        if dic[cursor] == 0:
            loops.pop()
        else:
            compiled_cont_cur = loops[-1]

    # implements the , command for jit
    def read():
        global dic
        global cursor

        if len(inp) <= inp_cur:
            #skips the input and sets the current cell to 0 if no input is found
            dic[cursor] = 0
        else:
            dic[cursor] = ord(inp[inp_cur])
            inp_cur += 1

    # implements the . command for jit
    def write():
        global dic
        global cursor

        print(chr(dic[cursor]), end='')



    # array to easily index the commands
    commands = [left, right, plus, minus, loop_s, loop_e, read, write]

    # executes the brainfuck script
    compiled_cont_cur = 0
    while compiled_cont_cur < compiled_cont_len:
        commands[compiled_cont[compiled_cont_cur]]()
        compiled_cont_cur += 1

    # ends programm
    sys.exit()




# length of the content read from file
cont_len = len(content)
# cursor to know where you are in the code
cont_cur = 0
# gets input from user to use later for ,
inp = input("Please Enter all Character the Program may need\n")

# interprets the language
while cont_cur < cont_len:
    c = content[cont_cur]

    match c:
        case "<":
            if cursor <= array_min:
                if wrap_array:
                    cursor = array_max
                elif out_of_bound_crash:
                    print("array out of bound at char " + cont_cur)
            else:
                cursor -= 1
            if cursor not in dic:
                dic[cursor] = init_value

        case ">":
            if cursor >= array_max:
                if wrap_array:
                    cursor = array_min
                elif out_of_bound_crash:
                    print("array out of bound at char " + cont_cur)
                    sys.exit()
            else:
                cursor += 1
            if cursor not in dic:
                dic[cursor] = init_value

        case "+":
            if dic[cursor] >= max_value:
                if wrap_array:
                    dic[cursor] = min_value
                elif value_too_big_crash:
                    print("value to big at char " + cont_cur)
                    sys.exit()
            else:
                dic[cursor] += 1

        case "-":
            if dic[cursor] <= min_value:
                if wrap_array:
                    dic[cursor] = max_value
                elif value_too_big_crash:
                    print("value to small at char " + cont_cur)
                    sys.exit()
            else:
                dic[cursor] -= 1

        case "[":
            if dic[cursor] != 0:
                loops.append(cont_cur)
            
            else:
                n_loop = -1 #to count how deep you are in the loop nesting
                while cont_cur < cont_len and (content[cont_cur] != ']' or n_loop > 0):
                    if content[cont_cur] == '[':
                        n_loop += 1
                    elif content[cont_cur] == ']':
                        n_loop -= 1
                    cont_cur += 1

        case "]":
            if dic[cursor] == 0:
                loops.pop()
            else:
                cont_cur = loops[-1]

        case ",":
            if len(inp) <= inp_cur:
                #skips the input and sets the current cell to 0 if no input is found
                dic[cursor] = 0
            else:
                dic[cursor] = ord(inp[inp_cur])
                inp_cur += 1

        case ".":
            print(chr(dic[cursor]), end='')

        case _:
            pass


    cont_cur += 1


#print(dic)