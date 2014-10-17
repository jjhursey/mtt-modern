# MTT Reporter - Script to extract JSON from v3php

This script accesses the last 24 hours of data and the default summary view from the "old reporter".
```
$ perl extract-json.pl
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  277k    0  277k    0     0  1326k      0 --:--:-- --:--:-- --:--:-- 1669k
$ ls *.json
flat.json pretty.json
```

The `flat.json` file is a JSON format without spacing or newlines.
The `pretty.json` file is the same data, but in a pretty printed format.


