#!/bin/env python3

import sys
import requests
import re

def get_sp_version(release: str) -> str:
    headers = {"Content-type": "application/json",
            "User-Agent": "Python"}

    resp = requests.get("https://repo.openeuler.org/", headers=headers)
    if resp.status_code != 200:
        sys.exit(1)

    r = re.compile('openEuler-{}(-LTS)?(-SP([0-9]))?'.format(release))

    ver = re.findall(r, resp.text)[-1][2]

    return ver if ver else '0'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('{} <release>'.format(sys.argv[0]))
        sys.exit(1)
    release = sys.argv[1]
    release = release.replace('.', '')
    print(release + '.' + get_sp_version(sys.argv[1]))