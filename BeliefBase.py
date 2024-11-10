import re
import cnf_py.run as toCNF
from sympy import symbols


class BeliefBase:
    def __init__(self) -> None:
        self.beliefBase = dict()

    def addBelief(self, belief, priority):
        # Transform logical cluase into logical clause in cnf format
        beliefCNF = self.ClauseToCNF(belief)
        # Get array of arrays from each clause between 'AND'
        arrayBelief = self.StringToArrayCNF(beliefCNF)
        # To forbidden adding same values
        if (beliefCNF in self.beliefBase):
            return False

        for orSequence in arrayBelief:
            # TODO: Remove a bug when there is a condtradiciton in the new belief(i.e (a and neg a))
            if (self.checkForContradiction(orSequence)):
                print("Contradiction found!!!!")
                return False

        print("WHOLE BELIEF WAS ADDED")
        self.beliefBase.update({belief: priority})
        print("NEW BELIEF BASE: ", self.beliefBase)

    def removeBelief(self, belief):
        if belief in self.beliefBase:
            self.beliefBase.pop(belief)
    def min_value_combination(self,dicts):
        common_keys = {}
        print(dicts)
        for idx, d in enumerate(dicts):
            for key in d:
                if key in common_keys:
                    common_keys[key].append(idx)
                else:
                    common_keys[key] = [idx]
        common_keys = {k: v for k, v in common_keys.items() if len(v) > 1}

        key_options = {}
        for key, indices in common_keys.items():
            value = dicts[indices[0]][key]
            key_options[key] = (value, indices)


        min_cost = sys.maxsize
        best_combination = None
        for comb in product([True, False], repeat=len(key_options)):
            cost = 0
            used = [False] * len(dicts)

            for selected, (key, (value, indices)) in zip(comb, key_options.items()):
                if selected:
                    cost += value
                    for idx in indices:
                        used[idx] = True

            if all(used):
                if cost < min_cost:
                    min_cost = cost
                    best_combination = comb

        if best_combination is not None:
            result = {key: value for (key, (value, _)), selected in zip(key_options.items(), best_combination) if
                      selected}
            return min_cost, result
        else:
            return None
    def ComputeBeliefPlan(self,ContractionPriority):
        min_cost, result = self.min_value_combination(ContractionPriority)
        print(min_cost)
        return min_cost, result
    def RemoveBelief(self,removedBelieves):
        for belief in removedBelieves:
            self.removeBelief(belief)

    def Contraction(self,newBelief):
        # print("NEW BELIEF: ", newBelief)

        if (len(self.beliefBase) == 0):
            # print("BELIEF WAS ADDED AS THE FIRST ELEMENT IN THE BELIEF BASE")
            return False
        # bufferBeliefBase = self.convertBeliefBaseToCNF()
        ContractionPriority=[]


        newBelief=self.ClauseToCNF(newBelief)

        newBelief = self.StringToArrayCNF(newBelief)
        newBelief = self.negateBelief(newBelief)
        for clauseSegment in newBelief:
            newclauseFlag = True
            print("*************clauseSegment",clauseSegment)
            Q={}
            Q_multi_team={}
            # clauseSegment = self.negateBelief([clauseSegment])[0]
            newBeliefSegment = clauseSegment
            for belief in self.beliefBase:

                newBeliefFlag = True
                originalBelief = belief
                print("*************oo", belief)
                belief = self.ClauseToCNF(belief)
                belief = self.StringToArrayCNF(belief)
                # print("******CNF", belief)

                for beliefSegment in belief:
                    print(beliefSegment, newBeliefSegment)
                    resolveResult=self.resolve(beliefSegment,newBeliefSegment)
                    if (resolveResult is not False):
                        if (len(resolveResult) == 0):
                            print("RESOLVED WITH SUCCESS , EMPTY BRACKET APPEAR\n")
                            if newBeliefFlag and newclauseFlag:
                                Q.update({originalBelief: self.beliefBase[originalBelief]})
                                break
                            else:
                                Q_multi_team.update({originalBelief: self.beliefBase[originalBelief]})
                                ContractionPriority.append(Q_multi_team)
                                print("*********Q_multi_team", Q_multi_team)
                                Q_multi_team = {}

                        elif (len(resolveResult) > 0):
                            # print("RESOLVED WITH SUCCESS ", resolveResult, "\n")
                            newBeliefSegment = resolveResult
                            Q_multi_team.update({originalBelief: self.beliefBase[originalBelief]})
                            newclauseFlag = False
                            break
                        else:
                            print("PAIR CANNOT BE RESOLVED\n")

                        self.RemoveBelief(Q)
                        print(ContractionPriority)
                        quit()
                        removedBelieves, removedPriority = self.ComputeBeliefPlan(ContractionPriority)

                        self.RemoveBelief(removedBelieves)

    def getBeliefSet(self):
        return self.beliefBase

        # Convert beliefBase into cnf format without repetitions

    def convertBeliefBaseToCNF(self):
        cnfBeliefBase = []
        for belief in self.beliefBase:
            belief = self.ClauseToCNF(belief)
            cnfBelief = self.StringToArrayCNF(belief)
            for partBelief in cnfBelief:
                if (cnfBelief not in cnfBeliefBase):
                    cnfBeliefBase.append(partBelief)
        return cnfBeliefBase

        # returns True - there is contradiction,
        # returns - False - no contradiction

    def checkForContradiction(self, newBelief):
        print("NEW BELIEF: ", newBelief)

        if (len(self.beliefBase) == 0):
            print("BELIEF WAS ADDED AS THE FIRST ELEMENT IN THE BELIEF BASE")
            return False

        newBelief = self.negateBelief([newBelief])

        buffNewBelief = newBelief
        bufferBeliefBase = self.convertBeliefBaseToCNF()

        print("NEGATED NEW BELIEF: ", newBelief, " BELIEF BASE: ", bufferBeliefBase, "\n")

        resolvedInLastIteration = True

        while (resolvedInLastIteration == True and len(bufferBeliefBase) > 0):
            for i in range(len(bufferBeliefBase)):
                print("BELIEF BASE AFTER RESOLVING: ", bufferBeliefBase)
                print("TOKEN FROM BELIEF BASE: ", bufferBeliefBase[i])
                print("NEW BELIEF: ", newBelief[0])
                resolveResult = self.resolve(newBelief[0], bufferBeliefBase[i])
                if (resolveResult is not False):
                    if (len(resolveResult) == 0):
                        print("RESOLVED WITH SUCCESS , EMPTY BRACKET APPEAR\n")
                        return False
                    elif (len(resolveResult) > 0):
                        print("RESOLVED WITH SUCCESS ", resolveResult, "\n")
                        newBelief = [resolveResult]
                        resolvedInLastIteration = True
                        bufferBeliefBase.pop(i)
                        break
                else:
                    print("PAIR CANNOT BE RESOLVED\n")
                    resolvedInLastIteration = False
        if (newBelief == buffNewBelief):
            return False
        if (bufferBeliefBase == []):
            return False
        return True

        # put in 2d array as the parameter

    def negateBelief(self, beliefs):
        symbols_list = symbols('a b c d')
        symbol_mapping_negative = {symbol: -symbol for symbol in symbols_list}
        symbol_mapping_negative.update({-symbol: symbol for symbol in symbols_list})
        negated_beliefs = [[symbol_mapping_negative.get(symbol, symbol) for symbol in row] for row in
                           beliefs]
        return negated_beliefs

        # non-cnf string into cnf string

    def ClauseToCNF(self, clause):
        resultClause = toCNF.run(clause)
        return resultClause[len(resultClause) - 1]

    # cnf string into cnf array
    def StringToArrayCNF(self, cnf_string):
        symbols_list = symbols('a b c d')
        symbol_mapping = {symbol.name: symbol for symbol in symbols_list}
        symbol_mapping_negative = {symbol.name: -symbol for symbol in symbols_list}

        clauses = cnf_string.split(' and ')

        literals = []
        for clause in clauses:
            clause_literals = []
            for match in re.finditer(r'\b(?:neg\s+)?([a-d])\b', clause):
                symbol = match.group(1)
                if match.group(0).startswith('neg'):
                    clause_literals.append(symbol_mapping_negative.get(symbol))
                else:
                    clause_literals.append(symbol_mapping.get(symbol))
            literals.append(clause_literals)

        return literals

    def resolve(self, clause1, clause2):
        set1 = set(clause1)
        set2 = set(clause2)
        Have_same_item_flag = 0

        for literal in set1:
            if -literal in set2:
                Have_same_item_flag = 1
                set1 = set1 - {literal}
                set2 = set2 - {-literal}
            elif literal in set2:
                Have_same_item_flag = 2

        if Have_same_item_flag == 0:
            return False
        else:
            new_clause = (set1 | set2)
            return list(new_clause)

a, b, c, d = symbols('a b c d')
bb = BeliefBase()

print(bb.convertBeliefBaseToCNF())

# print(bb.StringToArrayCNF(bb.ClauseToCNF("a imp b")))
bb.addBelief("a imp c", 1)
bb.addBelief("a imp b", 2)
bb.addBelief("a", 1000)
print(bb.getBeliefSet())
# quit()
bb.Contraction("b and c")

print(bb.getBeliefSet())