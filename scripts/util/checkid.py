import sys
import _root
import _helper

for id in sys.argv[1:]:
    ok = _helper.checkId(id, True)

    print(id, 'OK' if ok else 'ERROR')
