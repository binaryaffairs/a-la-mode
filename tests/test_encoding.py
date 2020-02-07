from a_la_mode import Task, Dag, sha, dissoc
from bencode import bencode
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