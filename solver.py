import copy
from collections import deque

# -------------------- READ BOARD --------------------

def read_board(filename):
    board = []
    with open(filename, 'r') as f:
        for line in f:
            board.append([int(ch) for ch in line.strip()])
    return board


def print_board(board):
    print("+-------+-------+-------+")
    for i in range(9):
        row = "| "
        for j in range(9):
            row += str(board[i][j]) + " "
            if (j + 1) % 3 == 0:
                row += "| "
        print(row)
        if (i + 1) % 3 == 0:
            print("+-------+-------+-------+")


# -------------------- VARIABLES & DOMAINS --------------------

def get_variables(board):
    return [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]


def get_initial_domains(board, variables):
    domains = {}
    for (r, c) in variables:
        possible = set(range(1, 10))

        for i in range(9):
            possible.discard(board[r][i])
            possible.discard(board[i][c])

        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(3):
            for j in range(3):
                possible.discard(board[br + i][bc + j])

        domains[(r, c)] = possible
    return domains


def get_neighbors(var, variables):
    r, c = var
    neighbors = set()

    for (nr, nc) in variables:
        if (nr, nc) == var:
            continue
        if nr == r or nc == c or (nr // 3 == r // 3 and nc // 3 == c // 3):
            neighbors.add((nr, nc))

    return neighbors


# -------------------- AC-3 --------------------

def revise(domains, xi, xj):
    revised = False
    for x in set(domains[xi]):
        if domains[xj] == {x}:
            domains[xi].remove(x)
            revised = True
    return revised


def ac3(domains, variables):
    queue = deque()

    for var in variables:
        for neighbor in get_neighbors(var, variables):
            queue.append((var, neighbor))

    while queue:
        xi, xj = queue.popleft()

        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False

            for xk in get_neighbors(xi, variables):
                if xk != xj:
                    queue.append((xk, xi))

    return True


# -------------------- BACKTRACKING --------------------

backtrack_calls = 0
backtrack_failures = 0


def select_unassigned_variable(assignment, variables, domains):
    unassigned = [v for v in variables if v not in assignment]
    return min(unassigned, key=lambda v: len(domains[v]))  # MRV


def is_consistent(var, value, assignment, variables):
    for neighbor in get_neighbors(var, variables):
        if neighbor in assignment and assignment[neighbor] == value:
            return False
    return True


def backtrack(assignment, variables, domains):
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    if len(assignment) == len(variables):
        return assignment

    var = select_unassigned_variable(assignment, variables, domains)

    for value in sorted(domains[var]):
        if is_consistent(var, value, assignment, variables):

            assignment[var] = value
            new_domains = copy.deepcopy(domains)
            new_domains[var] = {value}

            # Forward Checking
            failure = False
            for neighbor in get_neighbors(var, variables):
                if neighbor not in assignment:
                    new_domains[neighbor].discard(value)
                    if len(new_domains[neighbor]) == 0:
                        failure = True
                        break

            # AC-3 Propagation (IMPORTANT for marks)
            if not failure and ac3(new_domains, variables):
                result = backtrack(assignment, variables, new_domains)
                if result is not None:
                    return result

            del assignment[var]

    backtrack_failures += 1
    return None


# -------------------- SOLVE FUNCTION --------------------

def solve(filename):
    global backtrack_calls, backtrack_failures
    backtrack_calls = 0
    backtrack_failures = 0

    print("\n==============================")
    print("Solving:", filename)
    print("==============================")

    board = read_board(filename)
    print("\nOriginal:")
    print_board(board)

    variables = get_variables(board)
    domains = get_initial_domains(board, variables)

    print("\nRunning AC-3...")
    if not ac3(domains, variables):
        print("No solution!")
        return

    print("Running Backtracking...")
    result = backtrack({}, variables, domains)

    if result:
        for (r, c), val in result.items():
            board[r][c] = val

        print("\nSolved:")
        print_board(board)
    else:
        print("No solution found!")

    print("\nStats:")
    print("Backtrack calls:", backtrack_calls)
    print("Backtrack failures:", backtrack_failures)


# -------------------- MAIN --------------------

if __name__ == "__main__":
    boards = ["easy.txt", "medium.txt", "hard.txt", "veryhard.txt"]

    for b in boards:
        solve(b)

    print("\nAll boards solved!") 
