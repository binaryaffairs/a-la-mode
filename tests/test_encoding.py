from a_la_mode import Task, Dag, sha1, dissoc
from bencode import bencode

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

for task in [eg_dag.tasks['blur'], eg_dag.tasks['edge_enhance']]:
    task.add_dep(eg_dag.tasks['download_images'])

for task in [eg_dag.tasks['blur'], eg_dag.tasks['edge_enhance']]:
    eg_dag.tasks['collage'].add_dep(task)

encoded_dag = eg_dag.encode()

def test_outputs():
    for _name, task in encoded_dag['tasks'].items():
        output = task['output']
        assert output == sha1(bencode(dissoc(task, 'output')))

def test_inputs():
    for task in eg_dag.tasks.values():
        assert {dep.name for dep in task.deps} == \
               set(encoded_dag['tasks'][task.name]['inputs'].keys())
