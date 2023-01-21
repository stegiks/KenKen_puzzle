import sys
import functools
import csp
import time

def all_possible_doms(size, size_part):
    """
    Initialize the domain of each variable. The domain contains tuples
    of the set [1...board-size] that are of length 'clique-size'.
    Example in function generate_domains
    """

    """
    Creates a list of lists that contain all the possible values that a small box in the puzzle can take.
    The number of these lists is the number of the participants.
    """
    list1 = []
    for j in range(1, size_part + 1):
        list2 = []
        for i in range(1, size + 1):
            list2.append(i)
        list1.append(list2)
    
    """Generates a list of all possible combinations"""
    list_domains = [[]]
    for i in list1:
        new_list_domains = []
        for j in list_domains:
            for k in i:
                new_list_domains.append(j + [k])
        list_domains = new_list_domains
    
    """Makes the lists tuples"""
    list_domains_tuples = []
    for i in list_domains:
        list_domains_tuples.append(tuple(i))
    
    return list_domains_tuples 


def same_row_or_column(num_A, num_B, board_size):
    """
    Returns True if the 2 numbers are in same row or column. If the board size is 3 then the board looks like that:
     _______
    |       |
    | 0 1 2 |
    | 3 4 5 |
    | 6 7 8 |
    |_______|
    """
    if (abs(num_A-num_B) % board_size == 0) or (num_A // board_size == num_B // board_size): 
        return True
    else:
        return False 


def conflict(cl1, dom1, cl2, dom2, board_size):
    """
    If the variables have common row or column, same value and they aren't the same then they are conflicting 
    """
    part1 = cl1[1]
    part2 = cl2[1]
    size_part1 = len(part1)
    size_part2 = len(part2)

    for i in range(size_part1):
        for j in range(size_part2):
            val1 = dom1[i]
            val2 = dom2[j]
            if (same_row_or_column(part1[i], part2[j], board_size) and (part1[i] != part2[j]) and (val1 == val2)): 
                return True

    return False


def legal_operation(dom, operation, target):
    """
    A function that checks if the value is valid according to the target and the operation.
    """
    if operation == '=':
        return dom[0] == target
    else:
        if operation == '+':
            sum_part = sum(dom)
            return sum_part == target
        elif operation == '-':
            sub_part = abs(dom[0] - dom[1])
            return sub_part == target
        elif operation == '*':
            mult_part = 1
            for x in dom:
                mult_part = mult_part * x
            
            return mult_part == target
        else:
            div_part1 = dom[0]/dom[1]
            div_part2 = dom[1]/dom[0]
            return (div_part1 == target) or (div_part2 == target)


def generate_domains(list_cl, size):

    """
    Returns a dictionary that contains all the possible values that a clique 
    can take and agrees with the operation and target.
    If the size of var1 is 3, the size of the board is 4, operation is + and
    target is 7 then the values of this variable are like that:

    domain[var1] = [(1,3,3), (3,1,3), (3,3,1), ... , (4,1,2), (4,2,1)] 
    """
    domain = {}
    for cl in list_cl:
        target, participants, operation = cl
        size_part = len(participants)

        list_doms = []

        if size_part == 1:
            for l in range(1 , size + 1):
                list_doms.append((l,0))
        else:
            list_doms = all_possible_doms(size, size_part)

        real_list = []
        for element in list_doms:
            if legal_operation(element, operation, target):
                real_list.append(element)

        domain[cl] = real_list
    
    return domain
                

def generate_neighbors(list_cl, size):
    """
    If a variable can get a conflict with another, then they are considered as neighbors.
    This function returns a dictionary that each clique is key and the values are the neighbors. 
    """
    neighbors = {}
    for cl in list_cl:
        neighbors[cl] = []
    
    for cl1 in list_cl:
        
        for cl2 in list_cl:

            list_tup_1 = [0 for i in range(len(cl1[1]))]
            list_tup_2 = [0 for i in range(len(cl2[1]))]

            if cl1 != cl2 and conflict(cl1, list_tup_1, cl2, list_tup_2, size) and cl2 not in neighbors[cl1]:
                neighbors[cl1].append(cl2)
                neighbors[cl2].append(cl1)


    return neighbors

"""
It takes the input file and creates a list with the cliques. Cliques here are created as dictionaries with keys:
target, participants, operation
"""
def create_cliques(file_path):
    cliques = []

    with open(file_path, "r") as f:
        after_line_1 = f.readlines()[1:]

        for line in after_line_1:
            target, participants, operation = line.strip().split("#")

            cliques.append({
                "target": int(target),
                "participants": [int(x) for x in participants.split("-")],
                "operation": operation
            })
    return cliques


"""
Returns a dictionary that has as keys the positions(we take them from its participant)
of the puzzle and as items the values that the backtracking algorithm found for its position
"""
def create_participants_dict(result_dict = dict):
    part_dict = {}

    for keys, values in result_dict.items():
        target, participants, operator = keys

        size_of_part = len(participants)
        for i in range(size_of_part):
            if participants[i] not in part_dict.keys():
                part_dict[participants[i]] = values[i]
    
    return part_dict

"""
Returns a dictionary that has as keys the positions in the puzzle
and as items the values from the solution file
"""
def solution_dict(file_path):
    sol_dict = {}

    with open(file_path, "r") as f:
        count = 0

        for line in f:
            nums_of_line = [int(x) for x in line.strip().split()]

            for num in nums_of_line:
                sol_dict[count] = num
                count+= 1
    
    return sol_dict


class KenKen(csp.CSP):

    """
    We create a class that represents the game of KenKen as a CSP that can be solved with backtracking algorithms.
    The variables in this implementation are cliques. Cliques are in the form of a list that contains
    (target(int), participants of a clique(tuple with ints), operator(string)).
    """
    def __init__(self, cliques, size):

        self.size = size        #self.size is the size of the board
        var_s = cliques
        doms = generate_domains(cliques, size)
        neighs = generate_neighbors(cliques, size)
        csp.CSP.__init__(self, var_s, doms, neighs, self.constraints)

        self.conflicts = 0


    """
    If the value of a variable doesn't satisfy the target then it doesn't satisfy the constraints.
    Also if the 2 variables are conflicting, they don't satisfy the constraints.
    """
    def constraints(self, cl1, dom1, cl2, dom2):
        if conflict(cl1, dom1, cl2, dom2, self.size):
            self.conflicts+= 1
            return False
        return True 


def solve(file_puzzle):
    """
    Open the input file and split the lines. The first lines contains the size of the puzzle.
    After that it takes the remaining lines and exports a list that is explained in the class KenKen.
    """
    with open(file_puzzle, "r") as file:
        puzzle = file.read()
        lines = [line.strip() for line in puzzle]
        
    size = int(lines[0])
    cliques = create_cliques(file_puzzle)
    for x in cliques:
        x["participants"] = tuple(x["participants"])
        
    cliques = [tuple(dic.values()) for dic in cliques]

    # Create the CSP
    kenken_csp = KenKen(cliques, size)

    # Make partial functions with pre-specified arguments and use a switch dictionary
    back = functools.partial(csp.backtracking_search, kenken_csp)
    back_mrv = functools.partial(csp.backtracking_search, kenken_csp, csp.mrv)
    fc = functools.partial(csp.backtracking_search, kenken_csp, csp.first_unassigned_variable, csp.unordered_domain_values, csp.forward_checking)
    fc_mrv = functools.partial(csp.backtracking_search, kenken_csp, csp.mrv, csp.unordered_domain_values, csp.forward_checking)
    fc_mrv_lcv = functools.partial(csp.backtracking_search, kenken_csp, csp.mrv, csp.lcv, csp.forward_checking)
    mac = functools.partial(csp.backtracking_search, kenken_csp, csp.first_unassigned_variable, csp.unordered_domain_values, csp.mac)
    mac_mrv = functools.partial(csp.backtracking_search, kenken_csp, csp.mrv, csp.unordered_domain_values, csp.mac)
    mac_mrv_lcv = functools.partial(csp.backtracking_search, kenken_csp, csp.mrv, csp.lcv, csp.mac)

    switch_dict_algo = {
        1 : back,
        2 : back_mrv,
        3 : fc,
        4 : fc_mrv,
        5 : fc_mrv_lcv,
        6 : mac,
        7 : mac_mrv,
        8 : mac_mrv_lcv
    }

    print(
        "\nGive a number from 1 to 8 to choose an algorithm :\n"
        "1 : BACKTRACKING\n"
        "2 : BACKTRACKING + MRV\n"
        "3 : FC\n"
        "4 : FC + MRV\n"
        "5 : FC + LCV + MRV\n"
        "6 : MAC\n"
        "7 : MAC + MRV\n"
        "8 : MAC + LCV + MRV\n"
    )

    """Benchmarks test and solution"""

    input_algo = int(input())
    start = time.time()
    result = switch_dict_algo[input_algo]()
    end = time.time()

    print("\nExecution time of", input_algo ,"is : ", (end - start), "s")
    print("Assigns : ", kenken_csp.nassigns)
    print("Conflicts : ", kenken_csp.conflicts)

    dict_part = create_participants_dict(result)

    print("\nThe solution is :")
    print(dict_part, "\n")


if __name__ == "__main__":

    num_of_args = len(sys.argv)

    if num_of_args == 2:
        # If the user has given input file 
        input_file = sys.argv[1]
        solve(input_file)
    else:
        """
        Dictionary that represent switch case that other languages have.
        The user decides which puzzle to solve.
        """
        switch_dict_puzzles = {
            4 : "KenKen-4-Hard.txt",
            5 : "KenKen-5-Hard.txt",
            6 : "KenKen-6-Hard.txt",
            7 : "KenKen-7-Hard-1.txt",
            8 : "KenKen-8-Hard-1.txt",
            9 : "KenKen-9-Hard-1.txt" 
        }

        size_puzzle = int(input("\nGive a number from 4 to 9 for the size of the puzzle : "))
        if size_puzzle < 4 or size_puzzle > 9:
            print("Wrong size")
            sys.exit()

        file_puzzle = switch_dict_puzzles[size_puzzle]
        
        solve(file_puzzle)
