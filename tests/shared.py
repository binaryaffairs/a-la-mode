from a_la_mode import Dag
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
