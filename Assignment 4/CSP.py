import queue
import random
import copy

from typing import Set, Dict, List, TypeVar, Optional
from abc import ABC, abstractmethod

from util import monitor


Value = TypeVar('Value')


class Variable(ABC):
    @property
    @abstractmethod
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        pass

    def __copy__(self):
        return self

    def __deepcopy__(self, memodict={}):
        return self


class CSP(ABC):
    def __init__(self, MRV=True, LCV=True):
        self.MRV = MRV
        self.LCV = LCV

    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        """ Return the set of variables in this CSP.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def remainingVariables(self, assignment: Dict[Variable, Value]) -> Set[Variable]:
        """ Returns the variables not yet assigned. """
        return self.variables.difference(assignment.keys())

    @abstractmethod
    def neighbors(self, var: Variable) -> Set[Variable]:
        """ Return all variables related to var by some constraint.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def assignmentToStr(self, assignment: Dict[Variable, Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for var, val in assignment.items():
            s += f"{var} = {val}\n"
        return s

    def isComplete(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment covers all variables.
            :param assignment: dict (Variable -> value)
        """
        return not len(self.remainingVariables(assignment))

    @abstractmethod
    def isValidPairwise(self, var1: Variable, val1: Value, var2: Variable, val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass


    def isValid(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment is valid (i.e. is not in conflict with any constraints).
            You only need to take binary constraints into account.
            Hint: use `CSP::neighbors` and `CSP::isValidPairwise` to check that all binary constraints are satisfied.
            Note that constraints are symmetrical, so you don't need to check them in both directions.
        """
        for variable1 in self.variables-self.remainingVariables(assignment):
            for variable2 in self.neighbors(variable1)-self.remainingVariables(assignment):
                if not self.isValidPairwise(variable1, assignment[variable1], variable2, assignment[variable2]):
                    return False
        return True


    def solveBruteForce(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with brute force technique.
            Initializes the domains and calls `CSP::_solveBruteForce`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        return self._solveBruteForce(initialAssignment, domains)

    @monitor
    def _solveBruteForce(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm to brute force this CSP.
            Use `CSP::isComplete`, `CSP::isValid`, `CSP::selectVariable` and `CSP::orderDomain`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        if self.isComplete(assignment):
            return assignment
        var = self.selectVariable(assignment, domains)
        for value in self.orderDomain(assignment, domains, var):
            assignment[var] = value
            if self.isValid(assignment):
                result = self._solveBruteForce(assignment, domains)
                if result is not None:
                    return result
            assignment.pop(var)
        return None

    def solveForwardChecking(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking.
            Initializes the domains and calls `CSP::_solveForwardChecking`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        for var in set(initialAssignment.keys()):
            domains = self.forwardChecking(initialAssignment, domains, var)
        return self._solveForwardChecking(initialAssignment, domains)

    def checkEmptyDomain(self, domains: Dict[Variable, Set[Value]]):
        for domain in domains:
            if len(domains[domain]) == 0:
                return True
        return False


    @monitor
    def _solveForwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm with forward checking.
            Use `CSP::forwardChecking` and you should no longer need to check if an assignment is valid.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        if self.isComplete(assignment):
            return assignment
        var = self.selectVariable(assignment, domains)
        for value in self.orderDomain(assignment, domains, var):
            newAssignment = copy.deepcopy(assignment)
            newAssignment[var] = value
            newDomains = self.forwardChecking(newAssignment, domains, var)
            if self.checkEmptyDomain(newDomains):
                continue
            result = self._solveForwardChecking(newAssignment, newDomains)
            if result is not None:
                return result
        return None

    def forwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], variable: Variable) -> Dict[Variable, Set[Value]]:
        """ Implement the forward checking algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: The variable that was just assigned (only need to check changes).
        :return: the new domains after enforcing all constraints.
        """
        forwardDomains = copy.deepcopy(domains)
        for neighbor in self.neighbors(variable):
            for value in domains[neighbor]:
                if not self.isValidPairwise(variable, assignment[variable], neighbor, value):
                    forwardDomains[neighbor].remove(value)
        return forwardDomains

    def selectVariable(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Variable:
        """ Implement a strategy to select the next variable to assign. """
        if not self.MRV:
            return random.choice(list(self.remainingVariables(assignment)))

        variables = list(self.remainingVariables(assignment))
        fewestRemainingValues = variables[0]
        for var in variables[1:]:
            if len(domains[var]) < len(domains[fewestRemainingValues]):
                fewestRemainingValues = var
        return fewestRemainingValues

    def orderDomain(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], var: Variable) -> List[Value]:
        """ Implement a smart ordering of the domain values. """
        if not self.LCV:
            return list(domains[var])

        valuedict = {}
        for value in domains[var]:
            count = 0
            for neighbor in self.neighbors(var):
                for neighborValue in domains[neighbor]:
                    count += not self.isValidPairwise(var, value, neighbor, neighborValue)
            valuedict[value] = count
        return [item[0] for item in sorted(valuedict.items(), key=lambda x: x[1])]

    def solveAC3(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with AC3.
            Initializes domains and calls `CSP::_solveAC3`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        for var in set(initialAssignment.keys()):
            domains = self.ac3(initialAssignment, domains, var)
        return self._solveAC3(initialAssignment, domains)

    @monitor
    def _solveAC3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[Dict[Variable, Value]]:
        """
            Implement the actual backtracking algorithm with AC3.
            Use `CSP::ac3`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        if self.isComplete(assignment):
            return assignment
        var = self.selectVariable(assignment, domains)
        for value in self.orderDomain(assignment, domains, var):
            newAssignment = copy.deepcopy(assignment)
            newAssignment[var] = value
            newDomains = self.ac3(newAssignment, domains, var)
            if self.checkEmptyDomain(newDomains):
                continue
            result = self._solveAC3(newAssignment, newDomains)
            if result is not None:
                return result
        return None


    def ac3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], variable: Variable) -> Dict[Variable, Set[Value]]:
        """ Implement the AC3 algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: The variable that was just assigned (only need to check changes).
        :return: the new domains ensuring arc consistency.
        """
        newDomains = copy.deepcopy(domains)
        newDomains[variable] = {assignment[variable]}
        queue = []
        for var in self.neighbors(variable):
            queue.append((var, variable))

        while len(queue) > 0:
            (xi,xj) = queue.pop(0)
            if self.removeInconsistentValues(newDomains, xi, xj):
                for xk in self.neighbors(xi):
                    queue.append((xk,xi))
        return newDomains

    def removeInconsistentValues(self, domains: Dict[Variable, Set[Value]], xi, xj):
        removed = False
        for x in domains[xi].copy():
            satisfied = False
            for y in domains[xj]:
                if self.isValidPairwise(xi, x, xj, y):
                    satisfied = True
                    break
            if not satisfied:
                domains[xi].remove(x)
                removed = True
        return removed


def domainsFromAssignment(assignment: Dict[Variable, Value], variables: Set[Variable]) -> Dict[Variable, Set[Value]]:
    """ Fills in the initial domains for each variable.
        Already assigned variables only contain the given value in their domain.
    """
    domains = {v: v.startDomain for v in variables}
    for var, val in assignment.items():
        domains[var] = {val}
    return domains
