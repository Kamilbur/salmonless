# SRA Explorer

Python implementation of [SRA Explorer](https://sra-explorer.info) functionality.

## Usage

Number of search results can be massive, so it is always advisable to use `itertools.islice` for limiting this number.
```python
import itertools
from sra_explorer import SRAExplorer
for line in itertools.islice(SRAExplorer('liver'), 750):
    print(line)
```

```python
from sra_explorer import SRAExplorer
print(SRAExplorer('liver').experiment_count)
```