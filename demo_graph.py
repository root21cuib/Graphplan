from collections import defaultdict


class GraphPlan:
    def __init__(self, operators, initial_state, goals):
        self.operators = operators
        self.initial_state = initial_state
        self.goals = goals
        self.graph = defaultdict(list)
        self.solutions = []

    def expand_graph(self, level):
        self.graph[level] = self.graph[level - 1].copy()
        for operator in self.operators:
            if self.is_applicable(operator, level):
                self.apply_effects(operator, level)

    def is_applicable(self, operator, level):
        preconditions = operator['preconds']
        for precondition in preconditions:
            if precondition not in self.graph[level][-1]:
                return False
        return True

    def apply_effects(self, operator, level):
        effects = operator['effects']
        for effect in effects:
            if effect not in self.graph[level]:
                self.graph[level].append(effect)

    def extract_solution(self, level):
        solution = []
        i = level - 1
        while i >= 0:
            for operator in self.operators:
                all_effects_present = True
                for effect in operator['effects']:
                    if effect not in self.graph[i][-1]:
                        all_effects_present = False
                        break
                if all_effects_present:
                    solution.append(operator)
                    i -= 1
                    break
        return solution[::-1]  # Inversion du chemin pour obtenir le chemin optimal

    def save_solution_to_file(self, solution):
        with open('plan.txt', 'w') as file:
            file.write("/*----------------------------------------------------------------------------*/\n")
            file.write("/* ------------------------           Plan final      ------------------------*/\n")
            file.write("/*----------------------------------------------------------------------------*/\n\n")
            file.write("PLAN :\n\n")
            for operator in solution:
                params = operator['params']
                file.write(f"{operator['operator']}_{params[1]}_{params[0]}_{params[2]}\n")
            file.write("\n")

    def plan(self):
        self.graph[0].append(self.initial_state)
        self.graph[0].append(self.goals)
        level = 1
        while True:
            for i in range(level):
                if all(goal in self.graph[i][-1] for goal in self.goals):
                    solution = self.extract_solution(i)
                    self.save_solution_to_file(solution)  # Enregistrer la solution dans un fichier
                    self.solutions.append(solution)
                    return self.solutions
            self.expand_graph(level)
            level += 1

def parse_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    items = [line.strip() for line in lines if line.strip()]
    return items

def parse_operators(ops_file):
    operators = []
    current_operator = {}
    for line in ops_file:
        if line.startswith('(operator'):
            if current_operator:
                operators.append(current_operator)
            current_operator = {'operator': '', 'params': [], 'preconds': [], 'effects': []}
            current_operator['operator'] = line.split()
        elif line.startswith('('):
            parts = line.strip('()').split()
            if parts[0] == 'params':
                current_operator['params'] = parts[1:]
            elif parts[0] == 'preconds':
                current_operator['preconds'].append(tuple(parts[1:]))
            elif parts[0] == 'effects':
                current_operator['effects'].append(tuple(parts[1:]))
    if current_operator:
        operators.append(current_operator)
    return operators

def parse_facts(facts_file):
    facts = {'preconds': [], 'effects': []}
    current_section = 'preconds'
    for line in facts_file:
        if line.startswith('(effects'):
            current_section = 'effects'
        elif line.startswith('('):
            facts[current_section].append(tuple(line.strip('()').split()[1:]))
    return facts

def DoPlan(ops_file, facts_file):
    operators = parse_operators(ops_file)
    facts = parse_facts(facts_file)
    initial_state = facts['preconds']
    goals = facts['effects']
    planner = GraphPlan(operators, initial_state, goals)
    solutions = planner.plan()
    if solutions:
        for solution in solutions:
            print("Solution:")
            for operator in solution:
                print(operator)
            print()
    else:
        print("No solution found.")

# Exemple d'utilisation
if __name__ == "__main__":
    with open('r_ops.txt', 'r') as ops_file:
        ops_content = ops_file.readlines()
    with open('r_facts.txt', 'r') as facts_file:
        facts_content = facts_file.readlines()

    DoPlan(ops_content, facts_content)