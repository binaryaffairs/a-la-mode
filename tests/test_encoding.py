from a_la_mode import Task, Dag, sha, dissoc
from bencode import bencode
from toolz.dicttoolz import dissoc
import pytest

eg_dag = Dag({
    'schedule': '@daily'
})

eg_dag.task('download_images',
            {
                'image': 'collage',
                'sha': '1qe34',
                'command': "python dl_images.py"
            })

eg_dag.task('blur',
            {
                'image': 'collage',
                'sha': '6f09d',
                'command': "python transform_images.py blur"
            })

eg_dag.task('edge_enhance',
            {
                'image': 'collage',
                'sha': '1qe34',
                'command': "python transform_images.py edge_enhance"

            })

eg_dag.task('collage',
            {
                'image': 'collage',
                'sha': '1qe34',
                'command': "python collage.py"
            })

for task in [eg_dag.blur, eg_dag.edge_enhance]:
    task.add_dep(eg_dag.download_images)

for task in [eg_dag.blur, eg_dag.edge_enhance]:
    eg_dag.collage.add_dep(task)

encoded_dag = eg_dag.encode()
eg_dag.blur.spec['sha'] = 'qwetr3'

changed_dag = eg_dag
encoded_changed_dag = changed_dag.encode()

def test_unchanged():
    assert encoded_dag['meta'] == encoded_changed_dag['meta']
    for task in ['download_images', 'edge_enhance']:
        assert encoded_dag['tasks'][task] == encoded_changed_dag['tasks'][task]

def test_changed():
    # blurs sha and output changed
    assert encoded_dag['tasks']['blur']['sha'] != encoded_changed_dag['tasks']['blur']['sha']
    assert encoded_dag['tasks']['blur']['output'] != encoded_changed_dag['tasks']['blur']['output']

    # only blurs sha and output changed
    assert dissoc(encoded_dag['tasks']['blur'], 'sha', 'output') == \
           dissoc(encoded_changed_dag['tasks']['blur'], 'sha', 'output')

    # collages blur input changed
    assert encoded_dag['tasks']['collage']['inputs']['blur'] != \
           encoded_changed_dag['tasks']['collage']['inputs']['blur']

    # only collages blur input changed
    assert dissoc(encoded_dag['tasks']['collage']['inputs'], 'blur') == \
           dissoc(encoded_changed_dag['tasks']['collage']['inputs'], 'blur')

def test_outputs():
    for _name, task in encoded_dag['tasks'].items():
        output = task['output']
        assert output == sha(bencode(dissoc(task, 'output')))

def test_inputs():
    for task in eg_dag.tasks:
        assert {dep.name for dep in task.deps} == \
               set(encoded_dag['tasks'][task.name]['inputs'].keys())

def test_incorrect_task_name():
    with pytest.raises(AttributeError) as e_info:
        eg_dag.not_there