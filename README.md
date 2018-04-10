# edgar-analytics

1. [General Overview](https://github.com/kruti3/edgar-analytics/blob/master/README.md#general-overview)
2. [Instructions](https://github.com/kruti3/edgar-analytics/blob/master/README.md#instructions-to-run-the-code)

# General Overview

The solution implementation to this problem is similar to that of LRU cache. A queue and a map is maintained to keep a
track of incoming sessions in order and session object data details respectively at each instant.

A batch is defined as all sessions with last session time recorded at a particular second of time. Before processing a incoming batch, the expired sessions of previous batch(es) are removed. This is done by maintaining a variable which denotes the last session time associated with the batch and comparing it continually with incoming data to identify reduntant batches in data structures. The expired sessions are formatted to be written to the output and respective data is cleared from the data structures.

At the end of processing the entire input stream, few sessions remain in the data structures. These are then sorted by first session time and then last session time, and then formatted to the output file.

# Instructions to run the code

1. git clone https://github.com/kruti3/edgar-analytics.git
2. cd edgar-analytics
3. chmod 755 run.sh
4. ./run.sh

Instructions to run the tests: insight_testsuite/README.md

