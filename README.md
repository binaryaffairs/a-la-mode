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
successfully† been used before.

† Success detection is not trivial, something existing in the location is not
enough, some metadata or record of the task executions is needed.

# Example

If our workflow looks like this

![](https://raw.githubusercontent.com/binaryaffairs/a-la-mode/master/dag.png)


Create the 4 tasks

```python
from a_la_mode import Task, Dag, pp
from deepdiff import DeepDiff

dag = Dag({
    'schedule': '@daily'
})

dag.task('download_images',
            {
                'image': 'collage',
                'sha': '1qe34',
                'command': "python dl_images.py"
            })

dag.task('blur',
            {
                'image': 'collage',
                'sha': '6f09d',
                'command': "python transform_images.py blur"
            })

dag.task('edge_enhance',
            {
                'image': 'collage',
                'sha': '1qe34',
                'command': "python transform_images.py edge_enhance"

            })

dag.task('collage',
            {
                'image': 'collage',
                'sha': '1qe34',
                'command': "python collage.py"
            })
```

Connect them up with the basic DSL

```python
for task in [dag.blur, dag.edge_enhance]:
    task.add_dep(dag.download_images)

for task in [dag.blur, dag.edge_enhance]:
    dag.collage.add_dep(task)
```

encode the initial dag

```python
encoded_dag = dag.encode()
pp(encoded_dag)
```

```python
{ 'meta': {'schedule': '@daily'},
  'tasks': { 'blur': { 'command': 'python transform_images.py blur',
                       'image': 'collage',
                       'inputs': { 'download_images': '6075b3951568e2f31df204a59eb92bbb17d84e6b49f1275216bc0b6deb0e223d'},
                       'output': '82695e5805a9cd091e42ae94469efe77a90907c96190c793cee3c7d58dc2bbe0',
                       'sha': '6f09d'},
             'collage': { 'command': 'python collage.py',
                          'image': 'collage',
                          'inputs': { 'blur': '82695e5805a9cd091e42ae94469efe77a90907c96190c793cee3c7d58dc2bbe0',
                                      'edge_enhance': '7a764d984ce66d23a69c87645b47fcf7be79711f40be95fb631308ee01ca2a04'},
                          'output': '566a13d45eeebdefc50de118f5031278b20171ce76deb51791a4f084668e6d16',
                          'sha': '1qe34'},
             'download_images': { 'command': 'python dl_images.py',
                                  'image': 'collage',
                                  'inputs': {},
                                  'output': '6075b3951568e2f31df204a59eb92bbb17d84e6b49f1275216bc0b6deb0e223d',
                                  'sha': '1qe34'},
             'edge_enhance': { 'command': 'python transform_images.py '
                                          'edge_enhance',
                               'image': 'collage',
                               'inputs': { 'download_images': '6075b3951568e2f31df204a59eb92bbb17d84e6b49f1275216bc0b6deb0e223d'},
                               'output': '7a764d984ce66d23a69c87645b47fcf7be79711f40be95fb631308ee01ca2a04',
                               'sha': '1qe34'}}}
```

Change it and re-encode it after (this is just for demo, is not the expected usage)

```python
dag.blur.spec['sha'] = 'qwetr3'
encoded_changed_dag = dag.encode()
pp(encoded_changed_dag)
```

```python
{ 'meta': {'schedule': '@daily'},
  'tasks': { 'blur': { 'command': 'python transform_images.py blur',
                       'image': 'collage',
                       'inputs': { 'download_images': '6075b3951568e2f31df204a59eb92bbb17d84e6b49f1275216bc0b6deb0e223d'},
                       'output': '4df7200d1f836f7372ce01761c9cb9e0d2bc7d1abc7ee9c1abe8dc7df9a67e5e',
                       'sha': 'qwetr3'},
             'collage': { 'command': 'python collage.py',
                          'image': 'collage',
                          'inputs': { 'blur': '4df7200d1f836f7372ce01761c9cb9e0d2bc7d1abc7ee9c1abe8dc7df9a67e5e',
                                      'edge_enhance': '7a764d984ce66d23a69c87645b47fcf7be79711f40be95fb631308ee01ca2a04'},
                          'output': '25adad1924719ff4d5d2c3f4839f0ff1b4e21537c3c358f7d10b5e5d7c9c6de5',
                          'sha': '1qe34'},
             'download_images': { 'command': 'python dl_images.py',
                                  'image': 'collage',
                                  'inputs': {},
                                  'output': '6075b3951568e2f31df204a59eb92bbb17d84e6b49f1275216bc0b6deb0e223d',
                                  'sha': '1qe34'},
             'edge_enhance': { 'command': 'python transform_images.py '
                                          'edge_enhance',
                               'image': 'collage',
                               'inputs': { 'download_images': '6075b3951568e2f31df204a59eb92bbb17d84e6b49f1275216bc0b6deb0e223d'},
                               'output': '7a764d984ce66d23a69c87645b47fcf7be79711f40be95fb631308ee01ca2a04',
                               'sha': '1qe34'}}}
```

To save you time examining the output, we can take a look with DeepDiff

```python
pp(DeepDiff(encoded_dag, encoded_changed_dag))
```

```python
{ 'values_changed': { "root['tasks']['blur']['output']": { 'new_value': '4df7200d1f836f7372ce01761c9cb9e0d2bc7d1abc7ee9c1abe8dc7df9a67e5e',
                                                           'old_value': '82695e5805a9cd091e42ae94469efe77a90907c96190c793cee3c7d58dc2bbe0'},
                      "root['tasks']['blur']['sha']": { 'new_value': 'qwetr3',
                                                        'old_value': '6f09d'},
                      "root['tasks']['collage']['inputs']['blur']": { 'new_value': '4df7200d1f836f7372ce01761c9cb9e0d2bc7d1abc7ee9c1abe8dc7df9a67e5e',
                                                                      'old_value': '82695e5805a9cd091e42ae94469efe77a90907c96190c793cee3c7d58dc2bbe0'},
                      "root['tasks']['collage']['output']": { 'new_value': '25adad1924719ff4d5d2c3f4839f0ff1b4e21537c3c358f7d10b5e5d7c9c6de5',
                                                              'old_value': '566a13d45eeebdefc50de118f5031278b20171ce76deb51791a4f084668e6d16'}}}
```

You can see the sha and the output have changed for the `blur` task and the corresponding input to `collage` and its output are changed.



