from a_la_mode import Task, Dag, sha1, encode_dag, dissoc
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

def test_outputs():
    for _name, task in eg_dag.tasks.items():
        output = task.spec['output']
        assert output == sha1(bencode(dissoc(task.spec, 'output')))
