#!/usr/bin/env python3

"""Mininet tests for FAUCET fault-tolerance results.

 * must be run as root
 * you can run a specific test case only, by adding the class name of the test
   case to the command. Eg ./mininet_main.py FaucetUntaggedIPv4RouteTest

It is strongly recommended to run these tests via Docker, to ensure you have
all dependencies correctly installed. See ../docs/.
"""

import os
import networkx
from networkx.generators.atlas import graph_atlas_g

from clib.clib_mininet_test_main import test_main

import fault_tolerance_tests


def test_generator(func_graph, stack_roots):
    """Return the function that will start the fault-tolerance testing for a graph"""
    def test(self):
        """Test fault-tolerance of the topology"""
        self.set_up(func_graph, stack_roots)
        self.network_function()
    return test


if __name__ == '__main__':
    GRAPHS = {}
    GRAPH_ATLAS = graph_atlas_g()
    for graph in GRAPH_ATLAS:
        if (not graph
                or graph.number_of_nodes() > fault_tolerance_tests.MAX_NODES
                or graph.number_of_nodes() < fault_tolerance_tests.MIN_NODES):
            continue
        if networkx.is_connected(graph):
            GRAPHS.setdefault(graph.number_of_nodes(), [])
            GRAPHS[graph.number_of_nodes()].append(graph)
    TEST_LIMIT = int(os.getenv('FAUCET_GENERATIVE_LIMIT', '0'))

    def create_tests():
        """Create multi DP test variations."""
        test_count = 0
        for test_class in fault_tolerance_tests.TEST_CLASS_LIST:
            for test_graph in GRAPHS[test_class.NUM_DPS]:
                test_name = 'test_%s' % test_graph.name
                test_func = test_generator(test_graph, test_class.STACK_ROOTS)
                setattr(test_class, test_name, test_func)
                test_count += 1
                if TEST_LIMIT and test_count == TEST_LIMIT:
                    print('Limiting number of tests to', test_count)
                    return

    # TODO: because we are creating tests dynamically re-using the same base class,
    # we cannot run tests in parallel as tests with the same base class will
    # overwrite each other's metadata (including switch names).
    create_tests()
    test_main([fault_tolerance_tests.__name__], serial_override=True)
