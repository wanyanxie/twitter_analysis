__author__ = 'wanyanxie'

import matplotlib.pyplot as plt
import networkx as net
from collections import defaultdict
import math

twitter_network = [ line.strip().split('\t') for line in file('twitter_network.csv') ]

o = net.DiGraph()
hfollowers = defaultdict(lambda: 0)
for (twitter_user, followed_by, followers) in twitter_network:
    o.add_edge(twitter_user, followed_by, followers=int(followers))
    hfollowers[twitter_user] = int(followers)

SEED = 'usfca_analytics'

g = net.DiGraph(net.ego_graph(o, SEED, radius=4))


###  remove poorly connected nodes
def trim_degrees(g, degree=1):
    g2 = g.copy()
    d = net.degree(g2)
    for n in g2.nodes():
        if n == SEED: continue # don't prune the SEED node
        if d[n] <= degree:
            g2.remove_node(n)
    return g2

#### Remove edges that have less than a minimum number of followers
def trim_edges(g, weight=1):
    g2 = net.DiGraph()
    for f, to, edata in g.edges_iter(data=True):
        if f == SEED or to == SEED: # keep edges that link to the SEED node
            g2.add_edge(f, to, edata)
        elif edata['followers'] >= weight:
            g2.add_edge(f, to, edata)
    return g2


print 'g: ', len(g)
core = trim_degrees(g, degree= 15)
print 'core after node pruning: ', len(core)
core = trim_edges(core, weight= 50)
print 'core after edge pruning: ', len(core)

nodesets= [ n for n in core.nodes_iter()]
pos = net.spring_layout(core)

plt.figure(figsize=(20,20))
# plt.figure()
plt.axis('off')

# draw nodes
ns = [ math.log10(hfollowers[n]+1) * 300 for n in nodesets ]

net.draw_networkx_nodes(core, pos, nodelist=nodesets, node_size=ns,
                            node_color= 'green', alpha = 0.5)


#draw edges
net.draw_networkx_edges(core, pos, width=0.5, alpha=0.5)


# draw labels
for n in nodesets:
        x, y = pos[n]
        plt.text(x, y, s=n, alpha= 1.0, \
                 horizontalalignment='center', \
                 color='red', fontsize=10)

plt.savefig ('usf_msan_network.png')
plt.show()
