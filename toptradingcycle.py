from graph import *
from bson.objectid import ObjectId



# getAgents: graph, vertex -> set(vertex)
# get the set of agents on a cycle starting at the given vertex
def getAgents(G, cycle, agents):
   # a cycle in G is represented by any vertex of the cycle
   # outdegree guarantee means we don't care which vertex it is

   # make sure starting vertex is a house
   if cycle.vertexId in agents:
      cycle = cycle.anyNext()

   startingHouse = cycle
   currentVertex = startingHouse.anyNext() # the agent who lives in the house
   theAgents = set()

   while currentVertex not in theAgents:
      theAgents.add(currentVertex)
      currentVertex = currentVertex.anyNext() # house
      currentVertex = currentVertex.anyNext() # agent

   return theAgents


# anyCycle: graph -> vertex
# find any vertex involved in a cycle
def anyCycle(G): # return the vertex that represents some cycle of the graph
   visited = set() # empty set
   v = G.anyVertex() # random vertex

   while v not in visited:
      visited.add(v)
      v = v.anyNext()

   return v


# find a core matching of agents to houses
# agents and houses are unique identifiers for the agents and houses involved
# agentPreferences is a dictionary with keys being agents and values being
# lists that are permutations of the list of all houses.
# initiailOwnerships is a dict {houses:agents}
def topTradingCycles(agents, houses, agentPreferences, initialOwnership):
   # form the initial graph
   agents = set(agents)
   vertexSet = set(agents) | set(houses)
   G = Graph(vertexSet)
   #print (G)
   # maps agent to an index of the list agentPreferences[agent]
   currentPreferenceIndex = dict((a,0) for a in agents) # each agent prefer his first Preference
   preferredHouse = lambda a: agentPreferences[a][currentPreferenceIndex[a]] # a is one of agents list, update his preferedHouse by currentPreferenceIndex

   for a in agents:
      G.addEdge(a, preferredHouse(a)) # a prefers-> preferredHouse(a), example: add edge ('a',2)
   for h in houses: # h belongs to -> initialOwnership[h], example: add edge (2,'b')
      G.addEdge(h, initialOwnership[h])

   # iteratively remove top trading cycles
   allocation = dict()
   while len(G.vertices) > 0:
      cycle = anyCycle(G) # cycle its a vertex!
      cycleAgents = getAgents(G, cycle, agents)

      # assign agents in the cycle their house
      for a in cycleAgents:
         h = a.anyNext().vertexId
         allocation[a.vertexId] = ObjectId(h)
         G.delete(a)
         G.delete(h)

      for a in agents:
         if a in G.vertices and G[a].outdegree() == 0:
            while preferredHouse(a) not in G.vertices:
               currentPreferenceIndex[a] += 1
            G.addEdge(a, preferredHouse(a))
   # print(allocation)
   return allocation
