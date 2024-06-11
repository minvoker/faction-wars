import heapq

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def __lt__(self, other):
        return self.path_cost < other.path_cost

    def expand(self, get_neighbors, step_cost):
        return [self.child_node(get_neighbors, step_cost, action) for action in get_neighbors(self.state)]

    def child_node(self, get_neighbors, step_cost, action):
        next_state = action
        next_node = Node(next_state, self, action, self.path_cost + step_cost(self.state, action))
        return next_node

    def solution(self):
        return [node.action for node in self.path()]

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

class PriorityQueue:
    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        self.f = f
        self.order = 1 if order == 'min' else -1

    def append(self, item):
        heapq.heappush(self.heap, (self.f(item) * self.order, item))

    def pop(self):
        return heapq.heappop(self.heap)[1]

    def __contains__(self, item):
        return any(item == pair[1] for pair in self.heap)

def a_star_search(initial, goal, get_neighbors, step_cost, heuristic):
    '''
    Perform A* search with an explored set. This implementation uses a PriorityQueue as the frontier, 
    which stores tuples of (f(n), node) where f(n) = g(n) + h(n). 
    g(n) is the path cost and h(n) is the heuristic estimate (Manhattan Distance) of the cost from n to the goal state. 
    Returns a tuple containing the goal node and the number of nodes expanded during the search. 
    Returns None if no goal state is found.
    '''
    node = Node(initial)
    num_of_nodes = 1  # Count the initial node
    if node.state == goal:
        return node, num_of_nodes
    
    # Order based on f(n) = g(n) + h(n)
    frontier = PriorityQueue(order='min', f=lambda x: x[0])
    frontier.append((node.path_cost + heuristic(node.state, goal), node))
    explored = set()

    while frontier.heap:
        f_n, node = frontier.pop()

        if node.state not in explored:
            num_of_nodes += 1
            explored.add(node.state)
            if node.state == goal:
                return node, num_of_nodes

            for child in node.expand(get_neighbors, step_cost):
                child_f_n = child.path_cost + heuristic(child.state, goal)
                if child.state not in explored:
                    frontier.append((child_f_n, child))

    return None, num_of_nodes # Remove num_of_nodes after testing paths
