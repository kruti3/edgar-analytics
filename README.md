# edgar-analytics

1. [General Overview]
2. [Instructions]

# General Overview

The solution implementation to this problem is similar to that of LRU cache. A queue and a map is maintained to keep a
track of incoming sessions in order and session object data details respectively at each instant.

At the start of processing at the second of time, the expired sessions are given to the output, batch wise. Each batch
denotes all sessions with last session time at the second of time. The removal of expired sessions is done by
maintaining a variable which denotes the last batch time processed and comparing it continually with incoming data.

At the end, all the sessions remaining in the data structures is then sorted by first session time and then last session
time, and then formatted to the output file.

# Instructions to run the code

1. git clone https://github.com/kruti3/edgar-analytics.git
2. cd edgar-analytics
3. chmod 755 run.sh
4. ./run.sh

Instructions to run the tests: insight_testsuite/README.md

