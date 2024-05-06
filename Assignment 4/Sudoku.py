from typing import Set, Dict

from CSP import CSP, Variable, Value

regions = [[1, 1, 1, 2, 2, 2, 3, 3, 3],
           [1, 1, 1, 2, 2, 2, 3, 3, 3],
           [1, 1, 1, 2, 2, 2, 3, 3, 3],
           [4, 4, 4, 5, 5, 5, 6, 6, 6],
           [4, 4, 4, 5, 5, 5, 6, 6, 6],
           [4, 4, 4, 5, 5, 5, 6, 6, 6],
           [7, 7, 7, 8, 8, 8, 9, 9, 9],
           [7, 7, 7, 8, 8, 8, 9, 9, 9],
           [7, 7, 7, 8, 8, 8, 9, 9, 9]]

class Sudoku(CSP):
    def __init__(self, MRV=True, LCV=True):
        super().__init__(MRV=MRV, LCV=LCV)
        self._variables = []
        for x in range(9):
            row = []
            for y in range(9):
                row.append(Cell(x,y))
            self._variables.append(row)

    @property
    def variables(self) -> Set['Cell']:
        """ Return the set of variables in this CSP. """
        return {i for lst in self._variables for i in lst}


    def getCell(self, x: int, y: int) -> 'Cell':
        """ Get the  variable corresponding to the cell on (x, y) """
        return self._variables[x][y]

    def neighbors(self, var: 'Cell') -> Set['Cell']:
        """ Return all variables related to var by some constraint. """
        neighbors = set()
        xpos,ypos = var.Xpos,var.Ypos
        for x in range(9):
            for y in range(9):
                if x == xpos and y == ypos:
                    continue
                elif regions[x][y]==regions[xpos][ypos] or x == xpos or y == ypos:
                    neighbors.add(self._variables[x][y])
        return neighbors

    def isValidPairwise(self, var1: 'Cell', val1: Value, var2: 'Cell', val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp. """
        return not((regions[var1.Xpos][var1.Ypos]==regions[var2.Xpos][var2.Ypos] or var1.Xpos == var2.Xpos or var1.Ypos == var2.Ypos) and val1 == val2)

    def assignmentToStr(self, assignment: Dict['Cell', Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for y in range(9):
            if y != 0 and y % 3 == 0:
                s += "---+---+---\n"
            for x in range(9):
                if x != 0 and x % 3 == 0:
                    s += '|'

                cell = self.getCell(x, y)
                s += str(assignment.get(cell, ' '))
            s += "\n"
        return s

    def parseAssignment(self, path: str) -> Dict['Cell', Value]:
        """ Gives an initial assignment for a Sudoku board from file. """
        initialAssignment = dict()

        with open(path, "r") as file:
            for y, line in enumerate(file.readlines()):
                if line.isspace():
                    continue
                assert y < 9, "Too many rows in sudoku"

                for x, char in enumerate(line):
                    if char.isspace():
                        continue

                    assert x < 9, "Too many columns in sudoku"

                    var = self.getCell(x, y)
                    val = int(char)

                    if val == 0:
                        continue

                    assert val > 0 and val < 10, f"Impossible value in grid"
                    initialAssignment[var] = val
        return initialAssignment


class Cell(Variable):
    def __init__(self, Xpos, Ypos):
        super().__init__()
        self.Xpos = Xpos
        self.Ypos = Ypos

    @property
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        return set(range(1,10))


