#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function

import argparse
import sys
import vmprof


class FlameGraphPrinter:
    """
    The Flame Graph [1] printer for vmprof profile files.

    [1] http://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html
    """

    def show(self, profile):
        # (str) -> None
        """Read and display a vmprof profile file.

        :param profile: The filename of the vmprof profile file to convert.
        """
        try:
            stats = vmprof.read_profile(profile)
        except Exception as e:
            print("Fatal: could not read vmprof profile file '{}': {}".format(profile, e), file=sys.stderr)
            return
        tree = stats.get_tree()
        self.print_tree(tree)

    def _walk_tree(self, parent, node, level, lines):
        if ':' in node.name:
            split = node.name.split(':')
            funcname = split[1]
            rest = split[2:]
            if len(rest) >= 2:
                lineno = rest[0]
                filename = rest[1].split('/')[-1]
                funcname += ":{}:{}".format(filename, lineno)
            if parent:
                current = parent + ';' + funcname
            else:
                current = funcname
        else:
            current = node.name

        count = node.count

        level += 1
        for c in node.children.values():
            count -= c.count
            self._walk_tree(current, c, level, lines)

        lines.append((current, count))

    def print_tree(self, tree):
        lines = []
        self._walk_tree(None, tree, 0, lines)
        lines.sort()
        for p, c in lines:
            print(p, c)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    args = parser.parse_args()

    pp = FlameGraphPrinter()
    pp.show(args.profile)


if __name__ == '__main__':
    main()
