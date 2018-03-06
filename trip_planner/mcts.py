#!/usr/bin/env python
import numpy as np
from search_engine import search_engine
# MCTS scalar.  Larger scalar will increase exploitation, smaller will increase exploration.
EXPLORATION_CONSTANT = 1 / np.sqrt(2.0)

# import logging
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger('MyLogger')


class UCT(object):
    def __init__(self, initial_state, is_terminal):
        self.initial_state = initial_state
        self.root = Node(initial_state)
        self.is_terminal = is_terminal

    def search(self):
        state = self.initial_state.copy()
        leaf, state = self.select_leaf(state)
        state, simulated_actions = self.run_simulation(state)
        reward = self.get_reward(state)
        self.back_up(leaf, reward)
        return reward, leaf, simulated_actions
    #
    # def create_itinerary(self, actions):
    #     itinerary = []
    #     for action in actions:
    #         if action.target.IS_POI:
    #             place_id = action.target.data['place_id']
    #             place_type = "poi"
    #         else:
    #             place_id = action.target.data['owl:sameAs']
    #             place_type = "bus_stop"
    #         itinerary.append({
    #             "place_id": place_id,
    #             "place_type": place_type,
    #             "start_location": list(action.source.location),
    #             "end_location": list(action.target.location),
    #             "mode": action.mode,
    #             "route_id": action.route_id,
    #             "duration": action.duration
    #         })
    #     return itinerary



    def get_reward(self, state):
        return (state.total_poi_score - state.total_walking_cost) * state.total_bus_score * 1e-2


    def run_simulation(self, state):
        simulated_actions = []
        while self.is_terminal(state) == False:
            action = search_engine.get_action(state)
            if action is None:
                break
            state.step(action)
            simulated_actions.append(action)
        return state, simulated_actions


    def select_leaf(self, state):
        node = self.root
        while self.is_terminal(state) == False:
            if len(node.children) == 0 or (not node.is_fully_expanded() and np.random.random() < .8):
                return node.expand(state)
            node = node.find_urgent_child()
            if node.is_fully_expanded() and len(node.children) == 0:
                break
            state.step(node.action)
        return node, state


    def back_up(self, node, reward):
        while node != None:
            node.update(reward)
            node = node.parent
        return




class Node(object):
    def __init__(self, state, action=None, parent=None):
        self.visits = 1
        self.reward = 0.0
        self.action = action
        self.children = []
        stops, pois = search_engine.search_reachable_places(state)
        self.unexplored_stops = stops
        self.unexplored_pois = pois
        self.parent = parent

    def get_actions_from_root(self):
        actions = []
        node = self
        while node.action is not None:
            actions.append(node.action)
            node = node.parent
        return actions[::-1]

    def update(self, reward):
        self.reward += reward
        self.visits += 1

    def is_fully_expanded(self):
        if len(self.unexplored_pois) + len(self.unexplored_stops) > 0:
            return False
        return True

    def expand(self, state):
        # source = state.place
        action = search_engine.explore(state, self.unexplored_stops, self.unexplored_pois)
        state.step(action)
        child = Node(state, action, self)
        self.children.append(child)
        return child, state

    def find_urgent_child(self):
        best_score = -float('inf')
        children = []
        for child in self.children:
            q = child.reward / child.visits
            exploration_term = np.sqrt(2.0 * np.log(self.visits) / float(child.visits))
            ucb_score = q + EXPLORATION_CONSTANT * exploration_term
            if ucb_score == best_score:
                children.append(child)
            if ucb_score > best_score:
                children = [child]
                best_score = ucb_score

        return np.random.choice(children)

    def __repr__(self):
        level = len(self.get_actions_from_root())
        s = "Node; level: {:d} children: {:d} visits: {:d}; reward: {:.1f}".format(
            level, len(self.children), self.visits, self.reward / self.visits)
        return s

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='MCTS research code')
#     parser.add_argument('--num_sims', action="store", required=True, type=int)
#     parser.add_argument('--levels', action="store", required=True, type=int, choices=range(State.NUM_TURNS))
#     args = parser.parse_args()
#
#     current_node = Node(State())
#     for l in range(args.levels):
#         current_node = uct_search(args.num_sims / (l + 1), current_node)
#         print("level %d" % l)
#         print("Num Children: %d" % len(current_node.children))
#         for i, c in enumerate(current_node.children):
#             print(i, c)
#         print("Best Child: %s" % current_node.state)
#
#         print("--------------------------------")

