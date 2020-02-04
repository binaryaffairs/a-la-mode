# A La Mode

A tool for describing pure data pipelines that enables avoiding repeating work
(incrementality) and keeping old data around (provenance)

The DSL is inspired by airflow, the file generated is a
[bencoded](https://en.wikipedia.org/wiki/Bencode) description of the flow with
unique IDs for the outputs of each step, that will change if the task
description or any of its inputs change. What "output" means is left vague, you
might do files or folders on a local disk, blobs in Blob store, store them in a
database. 

The expectation is that different "execution engines" can parse this description
and perform the work described, avoiding outputting to locations that have
successfully† ran before

† Success detection is not trivial, something existing in the location is not
enough, some metadata or record of the task executions is needed.